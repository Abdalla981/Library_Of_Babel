# Library of Babel

## Description

This is a python implementation of the library of babel which is inspired by https://libraryofbabel.info/

The [*Library of Babel*](https://maskofreason.wordpress.com/wp-content/uploads/2011/02/the-library-of-babel-by-jorge-luis-borges.pdf) is a place imagined by Jorge Luis Borges in his collection *The Garden of Branching Paths*, published in 1941. In that masterpiece, Borges describes a universal library which contains all and every possible permuations of 410 pages of letters. This means, in effect, such library has everything that was ever written and anything that will ever be written.

Borges describes the immense knowledge such a library would contain, as it will have everything: *The Egyptians of Aeschylus*, The encylopedia Novalis, The precise description of quantum mechanis, the current consitution of Spain and even the true story of your death.

## Topology

The library topology is inspired from Borges's description where he outlines its structure as follows:

- Library is diveded into rooms of hexagonal shape
- Each hex has one entrance and one exit
- The remaining four walls contain five shelves each
- Each shelve has 32 books
- Each books contains 410 pages
- Each pages has 3200 characters

In the original description, Borges's uses 22 alphabets (since his mother tongue was spanish) but in this implementation 29 characters were uses; the 26 lowercase english alphabets, space, comma and full-stop. In effects this means that the library has $10^{4677}$ books. To put that in perspective, there are only $10^{80}$ atoms in the observable universe!

## Navigation

The library uses a commandline interface (v0.1) to provide navigation to the user. There are two functions available, browse and search. The browse function allows you to input the location of a certain pages, then it shows its contents to you. The search function allows you to input a text and it gives you its location in the library. Each page in the library has a location stamp as follows:

$X_1-wX_2-sX_3-bX_4-pX_5$

where $X_1$ is a base-36 number with a maximum length of 3003 to indicate the hex location, $X_2$ is the wall number between 1 and 4, $X_3$ is the shelve number between 1 and 5, $X_4$ is the book number between 1 and 32, and $X_5$ is the page number between 1 and 410.

Note: when using the save option, only the first 10 hex characters are used as the filename.

## Algorithm

This algorithm is not the same as in https://libraryofbabel.info/
Currently, the algorithm is not pseudo-random, which means that the library is perfectly ordered and perfectly determinitic in its contents. The contents of each page is not saved anywhere or generated on the spot (Given the number of books, no amount of matter in the observable universe can store even 0.000000000001% of its contents). 

The algorithm works by encoding the location of each page using its contents. Since we are using 29 characters and each page is has a permuation of these 29 characters, we end up with $29^{3200}$ different pages. Therefore, we can use a number with base-29 to encode its location with a maximum length of 3200. This means that a page content is its number as well. All what's left is to look up where that number is located given the library's topology.

The version found in https://libraryofbabel.info/ uses a determinitic and reversable pseudo-random number generator to shuffle the library into a seemingly random outlook. However, its contents are deterministic and thats how it can be consistant all the time.

Given the determinitc nature of the algorithm, one can argue that the library's contents are already written and are just waiting to be discovered.

## Installation

The libary is written in pure python, so additional dependencies are required beside python 3.10. Just clone and run!
