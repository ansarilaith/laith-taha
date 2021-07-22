# Deprecated

The FunBoard v1 is deprecated and this repository is not being maintained.

If you have a FunBoard v1, there is nothing wrong with it (I use mine all the time).
However, I am not having them made anymore and am not actively building this repositry.

Please use the images, software, and documentation for the [FunBoard v2](https://gitlab.com/duder1966/youtube-projects/-/tree/master/FunBoard/v2).

You can set up the latest funboard software like this:

1. Load the latest FunBoard **v2** image: [How to Load a MicroPython Image](https://gitlab.com/duder1966/youtube-projects/-/tree/master/FunBoard/v2/bin)
1. Connect to the REPL of your FunBoard **v1** board: []()
1. Push the RESET button and start pressing `ctrl-c` on the REPL.
1. When you get a Python prompt, type `with open('/lib/funboard/v1','w'): f.close()` and push ENTER two times. You are just creating a file `/lib/funboard/v1`.
1. Push the RESET button.
1. Your FunBoard should boot as v1. Watch the REPL for confirmation.


