#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <sys/socket.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/ipc.h>
#include <sys/msg.h>
#include <sys/shm.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

#include "vpx/vpx_codec.h"
#include "vpx/vpx_decoder.h"
#include "vpx/vp8dx.h"

#include "./tools_common.h"
#include "./video_reader.h"
#include "./vpx_config.h"



#define DEBUGPRINT

#ifdef DEBUGPRINT
#define DPRINT(format, arg...)  printf(format, ##arg)
#else
#define DPRINT(format, arg...) do{}while(0)
#endif


#define UDP_SERV_PORT (12345)
#define UDP_RECV_DATA_MAXLEN (65535)
#define IVF_HEADER_SIZE (12)

static const char *exec_name;

typedef struct raw_frame_data {
    size_t len;
    uint8_t *buf;
    unsigned int width;
    unsigned int height;
} RAWFRAMEDATA;

void usage_exit(void)
{
    // fprintf(stderr, "Usage: %s <infile> <outfile>\n", exec_name);
    exit(EXIT_FAILURE);
}


 void die(const char *fmt, ...) {
//   LOG_ERROR(NULL);
   usage_exit();
 }

void die_codec(vpx_codec_ctx_t *ctx, const char *s)
{
    const char *detail = vpx_codec_error_detail(ctx);

    printf("%s: %s\n", s, vpx_codec_error(ctx));
    if (detail) {
        printf("    %s\n", detail);
    }
    exit(EXIT_FAILURE);
}

#define VP8_FOURCC 0x30385056
#define VP9_FOURCC 0x30395056

static const VpxInterface vpx_decoders[] = {
#if CONFIG_VP8_DECODER
    { "vp8", VP8_FOURCC, &vpx_codec_vp8_dx },
#endif

#if CONFIG_VP9_DECODER
    { "vp9", VP9_FOURCC, &vpx_codec_vp9_dx },
#endif
};

int get_vpx_decoder_count(void)
{
    return sizeof(vpx_decoders) / sizeof(vpx_decoders[0]);
}

const VpxInterface *get_vpx_decoder_by_index(int i)
{
    return &vpx_decoders[i];
}

const VpxInterface *get_vpx_decoder_by_fourcc(uint32_t fourcc)
{
    int i;

    for (i = 0; i < get_vpx_decoder_count(); ++i) {
        const VpxInterface *const decoder = get_vpx_decoder_by_index(i);
        if (decoder->fourcc == fourcc) {
            return decoder;
        }
    }

    return NULL;
}

int vpx_img_plane_width(const vpx_image_t *img, int plane)
{
    if (plane > 0 && img->x_chroma_shift > 0) {
        return (img->d_w + 1) >> img->x_chroma_shift;
    } else {
        return img->d_w;
    }
}

int vpx_img_plane_height(const vpx_image_t *img, int plane)
{
    if (plane > 0 && img->y_chroma_shift > 0) {
        return (img->d_h + 1) >> img->y_chroma_shift;
    } else {
        return img->d_h;
    }
}

void vpx_img_write(const vpx_image_t *img, FILE *file)
{
    int plane;

    for (plane = 0; plane < 3; ++plane) {
        const unsigned char *buf = img->planes[plane];
        const int stride = img->stride[plane];
        const int w = vpx_img_plane_width(img, plane) *
                      ((img->fmt & VPX_IMG_FMT_HIGHBITDEPTH) ? 2 : 1);
        const int h = vpx_img_plane_height(img, plane);
        int y;

        for (y = 0; y < h; ++y) {
            fwrite(buf, 1, w, file);
            buf += stride;
        }
    }
}

//RAWFRAMEDATA* 
int vpx_img_write_to_buf(const vpx_image_t *img, RAWFRAMEDATA* vfd)
{
    uint8_t *vpx_frame_data_buf;
    size_t vpx_frame_data_len = 0;
    int plane;

    // if (NULL != vpx_frame_data_buf) {
    //     free(vpx_frame_data_buf);
    //     vpx_frame_data_buf = NULL;
    // }

    for (plane = 0; plane < 3; plane++) {
        size_t w = (size_t) (vpx_img_plane_width(img, plane) *
                             ((img->fmt & VPX_IMG_FMT_HIGHBITDEPTH) ? 2 : 1));
        size_t h = (size_t) vpx_img_plane_height(img, plane);
        vpx_frame_data_len += w * h;
    }

    //vfd = (RAWFRAMEDATA *) malloc(sizeof(RAWFRAMEDATA));
    //if (!vfd) {
    //    printf("vpx_img_write_to_buf malloc buf failed\n");
    //    return -1;
    //}

    //vpx_frame_data_buf=vfd->buf;
    vpx_frame_data_buf = (uint8_t *) malloc(vpx_frame_data_len * sizeof(uint8_t));
    //vfd->buf = (uint8_t *) malloc(vpx_frame_data_len * sizeof(uint8_t));
    if (!vpx_frame_data_buf) {
        printf("vpx_img_write_to_buf malloc buf failed\n");
        return -1;
    }
    uint8_t *dst_buf = vpx_frame_data_buf;

    for (plane = 0; plane < 3; ++plane) {
        const unsigned char *src_buf = img->planes[plane];
        const int stride = img->stride[plane];
        const int w = vpx_img_plane_width(img, plane) *
                      ((img->fmt & VPX_IMG_FMT_HIGHBITDEPTH) ? 2 : 1);
        const int h = vpx_img_plane_height(img, plane);
        int y;

        // DPRINT("vpx_img_write_to_buf: plane=%d src_buf=0x%x\n", plane, src_buf);
        for (y = 0; y < h; ++y) {
            // DPRINT("vpx_img_write_to_buf: memcpy y=%d\n", y);
            memcpy(dst_buf, src_buf, w);
            dst_buf += w;
            src_buf += stride;
        }
    }

    //DPRINT("vpx_img_write_to_buf finished! len = %ld vfd=0x%x\n", vpx_frame_data_len, vfd);
    //memcpy(vfd->buf, vpx_frame_data_buf, vpx_frame_data_len*sizeof(uint8_t));
    (vfd)->buf = vpx_frame_data_buf;
    //printf("0: %u\n",vfd->buf[1000]);
    (vfd)->len = vpx_frame_data_len;
    vfd->width= img->d_w;
    vfd->height= img->d_h;
    return 0;
}

void free_data(RAWFRAMEDATA *data){
  free(data->buf);
}

const VpxInterface *decoder = NULL;
vpx_codec_ctx_t codec;
int counter=0;
FILE *outfile = NULL;


int init_decoder(){
    vpx_codec_dec_cfg_t *dec_cfg = NULL;
    vpx_codec_flags_t dec_flags = 0;

    uint32_t VP80_fourcc_BE = 0x56503830;
    uint32_t VP80_fourcc_LE = 0x30385056;

    decoder = get_vpx_decoder_by_fourcc(VP80_fourcc_LE);
    if (!decoder) {
        perror("Unknown input codec.");
        exit(EXIT_FAILURE);
    }
    DPRINT("Using %s\n", vpx_codec_iface_name(decoder->codec_interface()));

    if ( vpx_codec_dec_init(&codec, decoder->codec_interface(), dec_cfg, dec_flags) ) {
        die_codec(&codec, "Failed to initialize decoder.");
    }
    return 0;

}

int set_outfile(const char* filename){
  printf("opening %s\n",filename);
    if (!(outfile = fopen(filename, "wb")))
      die("Failed to open %s for writing.", filename);

}

int decode_frame_and_write(uint8_t *recvdata, unsigned int frame_size ){

        if ( vpx_codec_decode(&codec, recvdata, frame_size, NULL, 0) ) {
            die_codec(&codec, "Failed to decode frame ");
        }
        vpx_image_t *img = NULL;
        vpx_codec_iter_t iter = NULL;
        img = vpx_codec_get_frame(&codec, &iter);
        vpx_img_write(img, outfile);
        counter++;
        return counter;
}

int decode_to_buffer(uint8_t *recvdata, unsigned int frame_size, RAWFRAMEDATA* data ){

        if ( vpx_codec_decode(&codec, recvdata, frame_size, NULL, 0) ) {
            die_codec(&codec, "Failed to decode frame ");
        }
        vpx_image_t *img = NULL;
        vpx_codec_iter_t iter = NULL;
        img = vpx_codec_get_frame(&codec, &iter);
        vpx_img_write_to_buf(img,data);
        return 0;
        //counter++;
        //return returncode;
}
