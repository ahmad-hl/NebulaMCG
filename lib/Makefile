all : decoder encoder
.PHONY : all
decoder: decoder.c
	gcc -shared -Wl,-soname,decoder -o decoder.so -L.  -lvpx -fPIC decoder.c
encoder: encoder.c
	gcc -shared -Wl,-soname,encoder -o encoder.so -L.  -lvpx -fPIC encoder.c
udp_frame_decoder: udp_frame_decoder.c
	gcc udp_frame_decoder.c -o udp_frame_decoder.so -lhiredis -L. -lvpx -fPIC -g
