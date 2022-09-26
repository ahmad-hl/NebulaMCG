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

#include <hiredis/hiredis.h>

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

typedef struct vpx_frame_data {
    size_t len;
    uint8_t *buf;
} VPXFRAMEDATA;

void usage_exit(void)
{
    // fprintf(stderr, "Usage: %s <infile> <outfile>\n", exec_name);
    exit(EXIT_FAILURE);
}


// void die(const char *fmt, ...) {
//   LOG_ERROR(NULL);
//   usage_exit();
// }

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

void vpx_img_write_to_fifo_pipe(const vpx_image_t *img, int fd)
{
    int plane;
    int sum = 0;

    for (plane = 0; plane < 3; ++plane) {
        const unsigned char *buf = img->planes[plane];
        const int stride = img->stride[plane];
        const int w = vpx_img_plane_width(img, plane) *
                      ((img->fmt & VPX_IMG_FMT_HIGHBITDEPTH) ? 2 : 1);
        const int h = vpx_img_plane_height(img, plane);
        int y;
        int res;

        DPRINT("vpx_img_write_to_fifo_pipe: plane=%d stride=%d w=%d h=%d \n", plane, stride, w, h);
        for (y = 0; y < h; ++y) {
            res = write(fd, buf, w);
            DPRINT("vpx_img_write_to_fifo_pipe: y=%d h=%d buf=0x%x res=%d\n", y, h, buf, res);
            buf += stride;
        }
        sum += stride * h;
    }
    DPRINT("vpx_img_write_to_fifo_pipe finished! total %d bytes.\n", sum);
}

VPXFRAMEDATA *vpx_img_write_to_buf(const vpx_image_t *img)
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

    VPXFRAMEDATA *vfd = (VPXFRAMEDATA *) malloc(sizeof(VPXFRAMEDATA));
    if (!vfd) {
        printf("vpx_img_write_to_buf malloc buf failed\n");
        return NULL;
    }

    vpx_frame_data_buf = (uint8_t *) malloc(vpx_frame_data_len * sizeof(uint8_t));
    if (!vpx_frame_data_buf) {
        printf("vpx_img_write_to_buf malloc buf failed\n");
        return NULL;
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

    DPRINT("vpx_img_write_to_buf finished! len = %ld vfd=0x%x\n", vpx_frame_data_len, vfd);
    // return vpx_frame_data_len;
    vfd->buf = vpx_frame_data_buf;
    vfd->len = vpx_frame_data_len;
    return vfd;
}



int main(int argc, char **argv)
{

    int sockfd;
    struct sockaddr_in servaddr, cliaddr;
    uint8_t recvdata[UDP_RECV_DATA_MAXLEN];
    int rdatalen = 0;
    unsigned int clilen = 0;
    struct timeval time_start, time_end;
    double decode_time = 0.0;
    FILE *outfile = NULL;
    const char *PIPE_PATH = "/tmp/vp8decode_fifo";
    int fd;

    vpx_codec_ctx_t codec;
    VpxVideoReader *reader = NULL;
    const VpxInterface *decoder = NULL;
    const VpxVideoInfo *info = NULL;
    vpx_codec_dec_cfg_t *dec_cfg = NULL;
    vpx_codec_flags_t dec_flags = 0;
    int frame_cnt = 1;
    int res = 0;
    long r_pipe_sz = 0;

    const int REDIS_PORT = 6379;

    uint8_t *vpx_frame_data_buf = NULL;
    size_t vpx_frame_data_len = 0;

    // init sockets
    sockfd = socket(PF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("socket create failed!");
        exit(EXIT_FAILURE);
    }

    bzero(&servaddr, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    servaddr.sin_port = htons(UDP_SERV_PORT);

    if ( bind(sockfd, (struct sockaddr *)&servaddr, sizeof(servaddr)) ) {
        perror("bind failed!");
        exit(EXIT_FAILURE);
    }


    // init fifo file
#ifdef USING_FIFO_PIPE
    res = remove(PIPE_PATH);
    if (-1 == res) {
        printf("remove fifo file failed!\n");
    }
    DPRINT("remove fifo file success!\n");

    res = mkfifo(PIPE_PATH, 0777);
    if (res != 0) {
        printf("mkfifo failed! res = %d\n", res);
        exit(EXIT_FAILURE);
    }
    DPRINT("mkfifo success! res = %d\n", res);

    /* block or nonblock ? */
    // fd = open(PIPE_PATH, O_RDWR|O_NONBLOCK);
    fd = open(PIPE_PATH, O_RDWR);
    if (fd < 0) {
        printf("fd < 0, exit...\n");
        exit(0);
    }
    DPRINT("open fifo file success! fd = %d \n", fd);

    r_pipe_sz = fcntl(fd, F_GETPIPE_SZ);
    DPRINT("pipe size = %ld bytes \n", r_pipe_sz);
    res = fcntl(fd, F_SETPIPE_SZ, 1048576);
    DPRINT("fcntl set pipesize : res = %d\n", res);
    r_pipe_sz = fcntl(fd, F_GETPIPE_SZ);
    DPRINT("pipe size = %ld bytes \n", r_pipe_sz);
#endif
    /*
        if (!(outfile = fopen("./outvideo.webm", "wb"))) {
            printf("Failed to open %s for writing.", PIPE_PATH);
            exit(EXIT_FAILURE);
        }
     */


    // init redis
    redisContext *rCtx = redisConnect("127.0.0.1", REDIS_PORT);
    if ((NULL != rCtx) && (rCtx->err)) {
        printf("Redis Error: %s\n", rCtx->errstr);
        redisFree(rCtx);
        exit(EXIT_FAILURE);
    }

    redisReply *rRly = redisCommand(rCtx, "FLUSHALL");
    if (NULL == rRly) {
        printf("Redis execute command:FLUSHALL failed! rRly == NULL\n");
        redisFree(rCtx);
        exit(EXIT_FAILURE);
    }
    // if (!((rRly->type == REDIS_REPLY_INTEGER) && (rRly->integer > 0))) {
    //     printf("Redis execute command:FLUSHALL failed!\n");
    //     redisFree(rCtx);
    //     exit(EXIT_FAILURE);
    // }
    freeReplyObject(rRly);


    // init decoding codec
    uint32_t VP80_fourcc_BE = 0x56503830;
    uint32_t VP80_fourcc_LE = 0x30385056;

    // DPRINT("VPX_DECODER_ABI_VERSION = %d\n", VPX_DECODER_ABI_VERSION);
    decoder = get_vpx_decoder_by_fourcc(VP80_fourcc_LE);
    if (!decoder) {
        perror("Unknown input codec.");
        exit(EXIT_FAILURE);
    }
    DPRINT("Using %s\n", vpx_codec_iface_name(decoder->codec_interface()));

    if ( vpx_codec_dec_init(&codec, decoder->codec_interface(), dec_cfg, dec_flags) ) {
        die_codec(&codec, "Failed to initialize decoder.");
    }


    // dealing with the frame data received from udp
    DPRINT("Ready to recv... \n");
    while (1) {
        memset(recvdata, 0, UDP_RECV_DATA_MAXLEN);
        rdatalen = recvfrom(sockfd, recvdata, UDP_RECV_DATA_MAXLEN, 0, (struct sockaddr *)&cliaddr,
                            &clilen);
        gettimeofday(&time_start, NULL);
        DPRINT(">recv %d data from %s:%d\n", rdatalen, inet_ntoa(cliaddr.sin_addr),
               ntohs(cliaddr.sin_port));

        vpx_codec_iter_t iter = NULL;
        vpx_image_t *img = NULL;

        unsigned int frame_size = 0;
        frame_size += (unsigned int) ((recvdata[0]));
        frame_size += (unsigned int) ((recvdata[1]) << 8);
        frame_size += (unsigned int) ((recvdata[2]) << 16);
        frame_size += (unsigned int) ((recvdata[3]) << 24);
        DPRINT(" frame_size: %d\n", frame_size);
        if ( vpx_codec_decode(&codec, &recvdata[IVF_HEADER_SIZE], frame_size, NULL, 0) ) {
            die_codec(&codec, "Failed to decode frame ");
        }
        while (NULL != (img = vpx_codec_get_frame(&codec, &iter))) {
            gettimeofday(&time_end, NULL);
            decode_time = ((time_end.tv_sec - time_start.tv_sec) * 1000000 +
                           (time_end.tv_usec = time_start.tv_usec)) / 1000;
            /* DPRINT(">recv %d data from %s:%d\n", rdatalen, inet_ntoa(cliaddr.sin_addr),
                    ntohs(cliaddr.sin_port)); */
            DPRINT("   frame:%d img: d_w=%d d_h=%d decode_time=%f ms\n",
                   frame_cnt, img->d_w, img->d_h, decode_time);
            // DPRINT("    img_fmt=%d img_cs=%d img_range=%d \n", img->fmt, img->cs, img->range);

            // TODO
            // VPXFRAMEDATA *vfd = (VPXFRAMEDATA*) malloc(sizeof(VPXFRAMEDATA));
            // DPRINT("vfd malloc\n");
            // vfd.len = 0;
            // vfd.buf = NULL;
            // DPRINT("vfd = 0x%x vfd.len=%d vfd.buf=0x%x\n", &vfd, vfd.len, vfd.buf);
            // VPXFRAMEDATA *vfdtmp = NULL;

            VPXFRAMEDATA *vfd =  vpx_img_write_to_buf(img);
            // DPRINT("vfd = 0x%x vfd->len=%d vfd->buf=0x%x\n", vfd, vfd->len, vfd->buf);

            rRly = redisCommand(rCtx, "LPUSH udp_vpx_frames %b", vfd->buf, vfd->len);
            if (NULL == rRly) {
                printf("redisCommand failed! frame_cnt = %d\n", frame_cnt);
                redisFree(rCtx);
                exit(EXIT_FAILURE);
            }
            if ((REDIS_REPLY_INTEGER == rRly->type)) {
                DPRINT("redisCommand reply integer = %d\n", rRly->integer);
            }
            freeReplyObject(rRly);
            free(vfd->buf);
            free(vfd);
            vfd = NULL;

            // vpx_img_write(img, outfile);
            // vpx_img_write_to_fifo_pipe(img, fd);
            ++frame_cnt;
        }
        // img = vpx_codec_get_frame(&decoder, &iter);
    }

    return 0;
}