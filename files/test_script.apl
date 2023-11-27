;; This is a comment

gosub "test"

hlt

_start-data_ ;; this is optional and its just for redirecting

;; subroutines are like functions but without arguments and return values, just goto's under the hood
subroutine "test"
	malloc 0, 20, string ;; allocate a chunk of memory starting at address 0 with the size of 20
	new_string string, "Hello\, world!\n" ;; set a string at the allocated heap
	put_string string ;; print the string
return

_end-data_
