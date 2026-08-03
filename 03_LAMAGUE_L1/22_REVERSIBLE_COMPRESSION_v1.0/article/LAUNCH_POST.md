We gave LAMAGUE a harder test than “can the symbols look compact?”

We froze 36 structured semantic packets, trained a
dictionary on 24, and tested it on 12
untouched packets.

Held-out result:

- 33.8% smaller than minified JSON with a shared dictionary
- 30.7% smaller including the codebook cost
- 36/36 exact round trips
- 324/324 constructed protected-loss mutations caught as expected

It is not arbitrary-language compression yet.

It is the first measured reversible semantic codec in the project.

**Compression That Refuses to Forget**
