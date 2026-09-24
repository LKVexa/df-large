/* Native regressions for the actual host CLI helpers. Run with ASan/UBSan. */
#define main brctl_original_main
#include "../vm/BOTTLE_ROCKET_4.7.0_COLUMNED_LCTL_VIRTUAL_DEVICE_IO_SERVICE_ARCHITECTURE_61K/host/brctl.c"
#undef main
#include <assert.h>
#include <dirent.h>

static int open_descriptors(void) {
    DIR *directory = opendir("/proc/self/fd");
    int count = 0;
    assert(directory);
    while (readdir(directory)) count++;
    assert(closedir(directory) == 0);
    return count;
}

int main(void) {
    char directory[] = "/tmp/df-large-host-XXXXXX";
    char image[256], key[256], private_key[256], public_key[256], mono[256];
    uint8_t *data = NULL, short_data[3] = {1, 2, 3}, secret[32] = {0};
    size_t size = 0;
    struct stat info;
    FILE *f;
    int fd;
    int before;
    br_posix_ctx context;
    uint64_t counter;
    assert(mkdtemp(directory));
    assert(snprintf(image, sizeof(image), "%s/image", directory) > 0);
    assert(snprintf(key, sizeof(key), "%s/key", directory) > 0);
    assert(snprintf(private_key, sizeof(private_key), "%s/private", directory) > 0);
    assert(snprintf(public_key, sizeof(public_key), "%s/public", directory) > 0);
    assert(snprintf(mono, sizeof(mono), "%s/image.mono", directory) > 0);

    assert(br_posix_adapter_init(&context, image) == 0);
    assert(save(mono, short_data, sizeof(short_data)) == 0);
    before = open_descriptors();
    for (int i = 0; i < 100; i++) assert(br_hal_posix.mr_(&context, &counter) != 0);
    assert(open_descriptors() == before);
    assert(unlink(mono) == 0);

    /* A buffered write can succeed while fclose fails flushing /dev/full. */
    assert(save("/dev/full", short_data, sizeof(short_data)) == -1);
    assert(save(image, short_data, sizeof(short_data)) == 0);
    assert(save(key, short_data, sizeof(short_data)) == 0);
    for (int i = 0; i < 100; i++) {
        assert(rawkey(key, secret) == -1);
        assert(inspect(image) == -1);
        assert(signimg(image, public_key, key) == -1);
        assert(verifyrun(image, key, 0) == -1);
    }
    assert(load(image, &data, &size) == 0 && size == 3);
    free(data);
    fd = open(image, O_WRONLY | O_TRUNC);
    assert(fd >= 0);
    assert(ftruncate(fd, BR_UPDATE_BYTES + 1) == 0);
    assert(close(fd) == 0);
    assert(load(image, &data, &size) == -1 && data == NULL && size == 0);

    assert(save(private_key, short_data, sizeof(short_data)) == 0);
    assert(keygen(private_key, public_key) == -1);
    assert(load(private_key, &data, &size) == 0 && size == sizeof(short_data));
    assert(memcmp(data, short_data, sizeof(short_data)) == 0);
    free(data);
    assert(access(public_key, F_OK) != 0);
    assert(unlink(private_key) == 0);
    assert(keygen(private_key, public_key) == 0);
    assert(stat(private_key, &info) == 0 && (info.st_mode & 0777) == 0600);
    assert(stat(public_key, &info) == 0 && info.st_size == 32);

    /* Explicit malformed key arguments must not fall back to default trust. */
    assert(statecmd("recover-state", image, key) == -1);
    assert(serve(image, key) == -1);
    f = fopen(image, "wb"); assert(f); assert(fclose(f) == 0);
    assert(unlink(image) == 0 && unlink(key) == 0);
    assert(unlink(private_key) == 0 && unlink(public_key) == 0);
    assert(rmdir(directory) == 0);
    puts("HOST_IO_REGRESSIONS_PASS");
    return 0;
}
