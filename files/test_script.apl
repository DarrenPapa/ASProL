gosub "start-up"
hlt

_start-data_

    auto_malloc 100, string
    new_string string, "Hello\n"
    put_string string

_end-data_
