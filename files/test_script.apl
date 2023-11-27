;; This is a comment

pointer address, 0
set address, 1
gosub "test"

_start-data_ ;; this is optional and its just for redirecting

subroutine "test"
	set *address, 101
return

_end-data_
