#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <dirent.h>

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <filename>\n", argv[0]);
        printf("Read files as root (restricted)\n");
        return 1;
    }

    // Block /etc/shadow
    if (strstr(argv[1], "/etc/shadow") != NULL) {
        printf("Access denied: Cannot read shadow file\n");
        return 1;
    }

    // Block root_flag_02 — only accessible via cron job
    if (strstr(argv[1], "root_flag_02") != NULL) {
        printf("Access denied: This flag requires a different approach\n");
        return 1;
    }

    struct stat path_stat;
    if (stat(argv[1], &path_stat) != 0) {
        printf("Error: Cannot access '%s'\n", argv[1]);
        return 1;
    }

    // If it's a directory, list its contents
    if (S_ISDIR(path_stat.st_mode)) {
        DIR *d = opendir(argv[1]);
        if (d == NULL) {
            printf("Error: Cannot open directory '%s'\n", argv[1]);
            return 1;
        }
        struct dirent *entry;
        while ((entry = readdir(d)) != NULL) {
            printf("%s\n", entry->d_name);
        }
        closedir(d);
        return 0;
    }

    FILE *f = fopen(argv[1], "r");
    if (f == NULL) {
        printf("Error: Cannot open file '%s'\n", argv[1]);
        return 1;
    }

    char buffer[4096];
    while (fgets(buffer, sizeof(buffer), f) != NULL) {
        printf("%s", buffer);
    }

    fclose(f);
    return 0;
}
