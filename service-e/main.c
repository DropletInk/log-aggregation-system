#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>

void current_time(char *buffer, size_t size) {
    time_t now = time(NULL);
    struct tm *t = localtime(&now);
    strftime(buffer, size, "%Y-%m-%d %H:%M:%S", t);
}

int main() {
    FILE *logfile = fopen("service-d.log", "a");

    if (!logfile) {
        perror("Failed to open log file");
        return 1;
    }

    int counter = 0;
    char timebuf[64];

    while (1) {
        current_time(timebuf, sizeof(timebuf));
        fprintf("%s | INFO | service-d | Processing job %d\n", timebuf, counter);
        fflush(stdout);  

        printf(logfile, "%s | INFO | service-d | Processing job %d\n", timebuf, counter);
        fflush(logfile);
        counter++;
        sleep(3);
    }

    fclose(logfile);
    return 0;
}
