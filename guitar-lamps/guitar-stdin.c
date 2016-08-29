#include <stdio.h>
#include <stdlib.h>
#include <linux/i2c-dev.h>
#include <fcntl.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <signal.h>

#define I2C_DEV "/dev/i2c-1"

#define NUNCHUCK_ADDR 0x52

#define MASK_BUTTON_Z 0x01
#define MASK_BUTTON_C 0x02
#define MASK_ACCEL_X 0x0C
#define MASK_ACCEL_Y 0x40
#define MASK_ACCEL_Z 0xC0

#define MASK_GREEN 0x10
#define MASK_RED 0x40
#define MASK_YELLOW 0x8
#define MASK_BLUE 0x20
#define MASK_ORANGE 0x80

#define BUTTON_Z(a) (a & MASK_BUTTON_Z)
#define BUTTON_C(a) ((a & MASK_BUTTON_C) >> 1)

#define ACCEL_X(a, b) ((a << 2) | ((b & MASK_ACCEL_X) >> 2))
#define ACCEL_Y(a, b) ((a << 2) | ((b & MASK_ACCEL_X) >> 4))
#define ACCEL_Z(a, b) ((a << 2) | ((b & MASK_ACCEL_X) >> 6))

int fd = 0;

#define GREEN "\033[32m"
#define RED "\033[31m"
#define YELLOW "\033[33m"
#define BLUE "\033[34m"
#define ORANGE "\033[35m"
#define WHITE "\033[37m"

void sigintHandler(int sigNum) {
        if (fd > 0) {
                close(fd);
        }

        psignal(sigNum, "");

        exit(0);
}

int init() {
        char buf[2];

        if ((fd = open(I2C_DEV, O_RDWR)) < 0) {
                return (-1);
        }

        if (ioctl(fd, I2C_SLAVE, NUNCHUCK_ADDR) < 0) {
                close(fd);
                return (-1);
        }

        buf[0] = 0xF0;
        buf[1] = 0x55;

        if (write(fd, buf, 2) < 0) {
                close(fd);
                return (-1);
        }

        buf[0] = 0xFB;
        buf[1] = 0x00;

        if (write(fd, buf, 2) < 0) {
                close(fd);
                return (-1);
        }

        return (0);
}

int readId(char *buf) {
        buf[0] = 0xFA;

        if (write(fd, buf, 1) < 0) {
                perror("write");
                close(fd);
                exit(1);
        }

        if (read(fd, buf, 6) < 0) {
                perror("read");
                close(fd);
                exit(1);
        }
}

int sendRequest() {
        char buf[1];

        buf[0] = 0x00;

        if (write(fd, buf, 1) < 0) {
                close(fd);
                return (-1);
        }
}

int readData(char *buf) {
        if (read(0, buf, 6) < 0) {
                return (-1);
        }

        return (0);
}

int main(int argc, char *argv[]) {
        char buf[6] = {0, 0, 0, 0, 0, 0};
        int accelX;
        int accelY;
        int accelZ;
        int buttonC;
        int buttonZ;
	int i;
	struct timeval tv;

        signal(SIGINT, sigintHandler);
        signal(SIGTERM, sigintHandler);

#if 0
        if (init() < 0) {
                perror("init");
                exit(1);
        }

        if (readId(buf) < 0) {
                perror("readId");
                close(fd);
                exit(1);
        }
#endif

     //   printf("0x%02x 0x%02x 0x%02x 0x%02x 0x%02x 0x%02x\n", buf[0], buf[1], buf[2], buf[3], buf[4], buf[5]);

        while (1) {
                if (readData(buf) < 0) {
                        perror("readData");
                        close(fd);
                        exit(1);
                }

	gettimeofday(&tv, NULL);
	printf("%d.%06d: ", tv.tv_sec, tv.tv_usec);
        printf("0x%02x 0x%02x 0x%02x 0x%02x 0x%02x 0x%02x\n", buf[0], buf[1], buf[2], buf[3], buf[4], buf[5]);
	if(buf[4]!=0xff) { printf("buf[4]: "); for(i=0; i<8; i++) if(!(buf[4] & (1<<i))) printf("%x ", 1<<i); puts(""); }
	if(buf[5]!=0xff) { printf("buf[5]: "); for(i=0; i<8; i++) if(!(buf[5] & (1<<i))) printf("%x ", 1<<i); puts(""); }
	if(!(buf[5] & MASK_GREEN)) printf("%s%s %s", GREEN, "GREEN", WHITE);
	if(!(buf[5] & MASK_RED)) printf("%s%s %s", RED, "RED", WHITE);
	if(!(buf[5] & MASK_YELLOW)) printf("%s%s %s", YELLOW, "YELLOW", WHITE);
	if(!(buf[5] & MASK_BLUE)) printf("%s%s %s", BLUE, "BLUE", WHITE);
	if(!(buf[5] & MASK_ORANGE)) printf("%s%s %s", ORANGE, "ORANGE", WHITE);
	puts("");
        //        printf("%d/%d", buf[0], buf[1]);

                //accelX = ACCEL_X(buf[2], buf[5]);
                //accelY = ACCEL_X(buf[3], buf[5]);
                //accelZ = ACCEL_X(buf[4], buf[5]);

              //  printf("; %d/%d/%d", accelX, accelY, accelZ);

                //buttonZ = BUTTON_Z(buf[5]);
                //buttonC = BUTTON_C(buf[5]);

               // printf ("; %s/%s", (buttonZ ? "z" : "Z"), (buttonC ? "c" : "C"));

               // printf("\n");

                //usleep(100 * 1000);
        }
}
