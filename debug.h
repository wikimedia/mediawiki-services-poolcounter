#ifdef DEBUG
    #define debug(fmt, ...) fprintf(stderr, "[poolcounter] DEBUG: " fmt, ##__VA_ARGS__)
#else
    #define debug(fmt, ...) do {} while(0)
#endif
