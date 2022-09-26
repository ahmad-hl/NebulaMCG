#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "vpx/vpx_encoder.h"
#include "vpx/vp8cx.h"

#include "./tools_common.h"
#include "./video_writer.h"

static const char *exec_name;

void usage_exit(void) {
  fprintf(stderr,
          "Usage: %s <codec> <width> <height> <infile> <outfile> "
          "<keyframe-interval> <error-resilient> <frames to encode>\n"
          "See comments in simple_encoder.c for more information.\n",
          exec_name);
  exit(EXIT_FAILURE);
}

typedef struct vpx_frame_data {
    size_t len;
    uint8_t *buf;
} VPXFRAMEDATA;

typedef struct raw_frame_data {
    size_t len;
    uint8_t *buf;
} RAWFRAMEDATA;

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



static const VpxInterface vpx_encoders[] = {
#if CONFIG_VP8_ENCODER
  { "vp8", VP8_FOURCC, &vpx_codec_vp8_cx },
#endif

#if CONFIG_VP9_ENCODER
  { "vp9", VP9_FOURCC, &vpx_codec_vp9_cx },
#endif
};

int get_vpx_encoder_count(void) {
  return sizeof(vpx_encoders) / sizeof(vpx_encoders[0]);
}
const VpxInterface *get_vpx_encoder_by_index(int i) { return &vpx_encoders[i]; }

const VpxInterface *get_vpx_encoder_by_name(const char *name) {
  int i;

  for (i = 0; i < get_vpx_encoder_count(); ++i) {
    const VpxInterface *encoder = get_vpx_encoder_by_index(i);
    if (strcmp(encoder->name, name) == 0) return encoder;
  }

  return NULL;
}

int vpx_img_plane_width(const vpx_image_t *img, int plane) {
  if (plane > 0 && img->x_chroma_shift > 0)
    return (img->d_w + 1) >> img->x_chroma_shift;
  else
    return img->d_w;
}

int vpx_img_plane_height(const vpx_image_t *img, int plane) {
  if (plane > 0 && img->y_chroma_shift > 0)
    return (img->d_h + 1) >> img->y_chroma_shift;
  else
    return img->d_h;
}


//int widths[] = {1920,1280,800,640,480};
//int heights[] = {1080,720,600,480,360};
//int bitrates[] = {5000000,2200000 , 1150000, 750000, 500000};
FILE *infile = NULL;
const VpxInterface *encoder = NULL;
vpx_codec_ctx_t *codec;
vpx_image_t *raw;
int keyframe_interval;
int frame_count=0;
int frames_encoded=0;

int init_encoder(int NUM_ENCODERS, int widths[], int heights[], int bitrates[]){
  encoder = get_vpx_encoder_by_name("vp8");
  if (!encoder) die("Unsupported codec.");

  keyframe_interval=10;
  VpxVideoInfo *info;
  info = calloc(NUM_ENCODERS,sizeof(VpxVideoInfo));
  vpx_codec_enc_cfg_t *cfg;
  cfg = calloc(NUM_ENCODERS,sizeof(vpx_codec_enc_cfg_t));

  codec = calloc(NUM_ENCODERS,sizeof(vpx_codec_ctx_t));
  raw = calloc(NUM_ENCODERS,sizeof(vpx_image_t));

  for(int i=0; i<NUM_ENCODERS;i++){
      //info[i] = { 0, 0, 0, { 0, 0 } };
      info[i].codec_fourcc = encoder->fourcc;
      info[i].frame_width = widths[i];
      info[i].frame_height = heights[i];
      info[i].time_base.numerator = 1;
      info[i].time_base.denominator = 30;

      if (info[i].frame_width <= 0 || info[i].frame_height <= 0 ||
          (info[i].frame_width % 2) != 0 || (info[i].frame_height % 2) != 0) {
        die("Invalid frame size: %dx%d", info[i].frame_width, info[i].frame_height);
      }

      if (!vpx_img_alloc(&(raw[i]), VPX_IMG_FMT_I420, info[i].frame_width,
                         info[i].frame_height, 1)) {
        die("Failed to allocate image.");
      }


      int res;
      res = vpx_codec_enc_config_default(encoder->codec_interface(), &(cfg[i]), 0);
      if (res) die_codec(&(codec[i]), "Failed to get default codec config.");

      cfg[i].g_w = info[i].frame_width;
      cfg[i].g_h = info[i].frame_height;
      cfg[i].g_timebase.num = info[i].time_base.numerator;
      cfg[i].g_timebase.den = info[i].time_base.denominator;
      cfg[i].rc_target_bitrate = bitrates[i];
      cfg[i].g_error_resilient = (vpx_codec_er_flags_t)0;
      if (vpx_codec_enc_init(&(codec[i]), encoder->codec_interface(), &(cfg[i]), 0))
        die_codec(&(codec[i]), "Failed to initialize encoder");

  }
}


vpx_codec_iter_t iter;
int vpx_img_read_from_data(vpx_image_t *img, RAWFRAMEDATA *data) {
  int plane;
  for (plane = 0; plane < 3; ++plane) {
    unsigned char *buf = img->planes[plane];
    const int stride = img->stride[plane];
    const int w = vpx_img_plane_width(img, plane) *
                  ((img->fmt & VPX_IMG_FMT_HIGHBITDEPTH) ? 2 : 1);
    const int h = vpx_img_plane_height(img, plane);
    int y;

    memcpy(buf,data->buf,w*h);
    data->buf+=stride*h;
  }

  return 1;
}

int encode_frame_from_data(RAWFRAMEDATA *data, int index,int kf) {

    if(vpx_img_read_from_data(&(raw[index]), data)){
        int flags = 0;
        if (keyframe_interval > 0 && frame_count % keyframe_interval == 0 || kf==1){
            flags |= VPX_EFLAG_FORCE_KF;
            flags |= VP8_EFLAG_NO_REF_LAST;
            flags |= VP8_EFLAG_NO_REF_GF;
        }
        frame_count++;
        int got_pkts = 0;
        //vpx_codec_iter_t iter = NULL;
        iter = NULL;
        const vpx_codec_err_t res =
            vpx_codec_encode(&(codec[index]), &(raw[index]), frame_count, 1, flags, VPX_DL_REALTIME);
        if (res != VPX_CODEC_OK) die_codec(&(codec[index]), "Failed to encode frame");
        return 0;

    }

    return -1;
}

int get_encoded_frame(VPXFRAMEDATA *data,int index)
{
    const vpx_codec_cx_pkt_t *pkt = NULL;
    if((pkt = vpx_codec_get_cx_data(&(codec[index]), &iter)) != NULL) {
      //printf("Debug1,%i\n",pkt->kind);
      if (pkt->kind == VPX_CODEC_CX_FRAME_PKT) {
        const int keyframe = (pkt->data.frame.flags & VPX_FRAME_IS_KEY) != 0;
        data->len=pkt->data.frame.sz;
        data->buf=pkt->data.frame.buf;
          //printf(keyframe ? "K" : ".");
          //fflush(stdout);

      }
      return 1;
    }
    return 0;
}

