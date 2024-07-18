import math
import os
import random
import sys
from dataclasses import dataclass
from typing import Tuple

sys.set_int_max_str_digits(0)

hexs = {}
books = {}
ALPHABET = "abcdefghijklmnopqrstuvwxyz ,."
HEX_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"


class BaseX:
    def __init__(self, alphabet):
        self.alphabet = alphabet
        self.alphabet_dict = dict((c, i) for i, c in enumerate(alphabet))
        self.base = len(alphabet)

    def encode(self, num):
        """Encode a positive number into Base X and return the string.

        Arguments:
        - `num`: The number to encode
        """
        if num == 0:
            return self.alphabet[0]

        length = len(self.alphabet)
        ret = ""
        while num != 0:
            ret = self.alphabet[num % length] + ret
            # For Python 2 use /= instead of //=:
            # integer /= length
            num //= length

        return ret

    def decode(self, string):
        """Decode a Base X encoded string into the number

        Arguments:
        - `string`: The encoded string
        """
        length = len(self.alphabet_dict)
        ret = 0
        for i, c in enumerate(reversed(string)):
            ret += (length**i) * self.alphabet_dict[c]

        return ret


class Size:

    def __init__(self, value: int, remainder: int, div: int) -> None:
        self.value = value
        self.remainder = remainder
        self.div = div

    def __repr__(self) -> str:
        if self.value < 10e10:
            return str(self.value)
        else:
            return f"10e+{math.log10(self.value):.0f}"


@dataclass
class Location:
    hex_id: str
    wall_id: int
    shelve_id: int
    book_id: int
    page_id: int


@dataclass
class LibraryTopology:
    no_of_alphabets: int
    chars_per_page: int = 3200
    pages_per_book: int = 410
    books_per_shelve: int = 32
    shelves_per_wall: int = 5
    walls_per_hex: int = 4

    @property
    def pages_per_shelve(self):
        return self.pages_per_book * self.books_per_shelve

    @property
    def pages_per_wall(self):
        return self.pages_per_shelve * self.shelves_per_wall

    @property
    def pages_per_hex(self):
        return self.pages_per_wall * self.walls_per_hex


class Library:
    start_screen_text = (
        40 * "*"
        + "Welcome to the library of babel."
        + 40 * "*"
        + "\n\nThis is a python implementation of the library of babel which was "
        "inspired from: https://libraryofbabel.info/\n\n"
    )
    main_menu_text = (
        "Please choose one of the options below:\n1. Browse (1)\n"
        "2. Search (2)\n3. Random page (3)\n4. Print topology (4)\n\nQuit (-1)\n\n"
    )
    browse_menu_hex_text = (
        "Please specify the location of the hex "
        "(combination of 3003 alphanumerical values a - z and 1 - 9): "
    )
    browse_menu_wall_text = "Please specify the location of the wall (1, 2, 3 or 4): "
    browse_menu_shelve_text = (
        "Please specify the location of the shelve (1, 2, 3, 4 or 5): "
    )
    browse_menu_book_text = "Please specify the location of the wall (1 - 32): "
    browse_menu_page_text = "Please specify the location of the wall (1 - 410): "
    browse_menu_result_text = (
        "\n\nThe text on the page is\n\n %s \n\nPlease choose one "
        "of the following options:\n1. Browse again (1)\n2. Return to Main Menu (2)\n"
        "3. Next page (3)\n4. Previous page (4)\n5. Save (5)\n\nQuit (-1)\n\n"
    )
    browse_book_text = (
        "Book location: %s\n\n%s\n\nPlease choose an option from below:"
        "\n1. Next page (1)\n2. Previous page (2)\n3. Return to Main Menu (3)"
        "\n4. Save result (4)\nQuit (-1)\n\n"
    )
    search_menu_text = (
        "Please specify the text you are searching for " "(3200 characters max):\n\n"
    )
    search_menu_result_text = (
        "\n\nThe following text:\n\n%s\n\nis found on page %s of book %s on shelve %s. "
        "The shelve is found by wall %s in hex %s\nLocation: %s\n\nPlease choose one "
        "of the following options:\n1. Search again (1)\n2. Return to Main Menu (2)\n"
        "3. Next Page (3)\n4. Previous Page (4)\n5. Save (5)\n\nQuit (-1)\n\n"
    )
    random_menu_text = (
        "\n\nThe following is a random page in the library:\n\n%s\n\nis found on page "
        "%s of book %s on shelve %s. The shelve is found by wall %s in hex %s\n"
        "Location: %s\n\nPlease choose one of the following options:\n1. Random again "
        "(1)\n2. Return to Main Menu (2)\n3. Next Page (3)\n4. Previous Page (4)\n"
        "5. Save (5)\n\nQuit (-1)\n\n"
    )
    print_topology_text = (
        "The library topology is as follow:\n\n%s\n\nPlease choose "
        "one of the following:\n1. Go back to Main Menu (1)\n\nQuit (-1)\n\n"
    )

    def __init__(self, alphabet=ALPHABET, hex_alphabet=HEX_ALPHABET) -> None:
        self.alphabet = alphabet
        self.hex_alphabet = hex_alphabet
        self.conversion = BaseX(alphabet=alphabet)
        self.hex_conversion = BaseX(alphabet=hex_alphabet)
        self.init_stats()

    def init_stats(self) -> None:
        self.topology = LibraryTopology(no_of_alphabets=len(self.alphabet))
        self.no_of_pages = Size(
            value=self.topology.no_of_alphabets**self.topology.chars_per_page,
            remainder=0,
            div=1,
        )
        self.no_of_books = Size(
            value=self.no_of_pages.value // self.topology.pages_per_book,
            remainder=self.no_of_pages.value % self.topology.pages_per_book,
            div=self.topology.pages_per_book,
        )
        self.no_of_shelves: Size = Size(
            value=self.no_of_pages.value // self.topology.pages_per_shelve,
            remainder=self.no_of_pages.value % self.topology.pages_per_shelve,
            div=self.topology.pages_per_shelve,
        )
        self.no_of_walls: Size = Size(
            value=self.no_of_pages.value // self.topology.pages_per_wall,
            remainder=self.no_of_pages.value % self.topology.pages_per_wall,
            div=self.topology.pages_per_wall,
        )
        self.no_of_hexes: Size = Size(
            value=self.no_of_pages.value // self.topology.pages_per_hex,
            remainder=self.no_of_pages.value % self.topology.pages_per_hex,
            div=self.topology.pages_per_hex,
        )

    def run(self) -> None:
        self.clear_screen()
        print(self.start_screen_text)
        while True:
            print(self.main_menu_text)
            user_input = input()
            if user_input == "-1":
                exit()
            if user_input == "1":
                self.browse()
            if user_input == "2":
                self.search()
            if user_input == "3":
                self.random()
            if user_input == "4":
                self.print_topology()
            self.clear_screen()

    def browse(self) -> None:
        while True:
            self.clear_screen()
            location = self.get_location_from_user()
            text, stamp = self.get_page_content(location)
            print(self.browse_menu_result_text % text)
            user_input = input()
            if user_input == "-1":
                exit()
            if user_input == "1":
                continue
            if user_input == "2":
                break
            if user_input == "3":
                next_location = self.next(location)
                self.browse_book(next_location)
                break
            if user_input == "4":
                prev_location = self.previous(location)
                self.browse_book(prev_location)
                break
            if user_input == "3":
                self.save_result(self.browse_menu_result_text % text, stamp)
                break

    def search(self) -> None:
        while True:
            self.clear_screen()
            text = self.get_user_input(self.search_menu_text, "str", bound=3200)
            text = self.normalise_text(text)
            location = self.get_location_from_text(text)
            stamp = self.get_stamp(location)
            result = self.search_menu_result_text % (
                text,
                location.page_id,
                location.book_id,
                location.shelve_id,
                location.wall_id,
                location.hex_id,
                stamp,
            )
            print(result)
            user_input = input()
            if user_input == "-1":
                exit()
            if user_input == "1":
                continue
            if user_input == "2":
                break
            if user_input == "3":
                next_location = self.next(location)
                self.browse_book(next_location)
                break
            if user_input == "4":
                prev_location = self.previous(location)
                self.browse_book(prev_location)
                break
            if user_input == "5":
                self.save_result(result, stamp)
                break

    def random(self):
        while True:
            self.clear_screen()
            page_no = random.randint(0, self.no_of_pages.value)
            text = self.conversion.encode(page_no)
            location = self.get_location_from_text(text)
            stamp = self.get_stamp(location)
            result = self.random_menu_text % (
                text,
                location.page_id,
                location.book_id,
                location.shelve_id,
                location.wall_id,
                location.hex_id,
                stamp,
            )
            print(result)
            user_input = input()
            if user_input == "-1":
                exit()
            if user_input == "1":
                continue
            if user_input == "2":
                break
            if user_input == "3":
                next_location = self.next(location)
                self.browse_book(next_location)
                break
            if user_input == "4":
                prev_location = self.previous(location)
                self.browse_book(prev_location)
                break
            if user_input == "5":
                self.save_result(result, stamp)
                break

    def browse_book(self, location: Location):
        while True:
            self.clear_screen()
            text, stamp = self.get_page_content(location)
            print(self.browse_book_text % (stamp, text))
            user_input = input()
            if user_input == "1":
                next_location = self.next(location)
                self.browse_book(next_location)
                break
            if user_input == "2":
                prev_location = self.previous(location)
                self.browse_book(prev_location)
                break
            if user_input == "3":
                break
            if user_input == "4":
                self.save_result(self.browse_book_text % (stamp, text), stamp)
                break
            if user_input == "-1":
                exit()

    def print_topology(self) -> None:
        while True:
            self.clear_screen()
            print(self.print_topology_text % self)
            user_input = input()
            if user_input == "-1":
                exit()
            if user_input == "1":
                break

    def next(self, location: Location) -> Location:
        if location.page_id < self.topology.pages_per_book:
            location.page_id += 1
        elif location.book_id < self.topology.books_per_shelve:
            location.page_id = 1
            location.book_id += 1
        elif location.shelve_id < self.topology.shelves_per_wall:
            location.page_id = 1
            location.book_id = 1
            location.shelve_id += 1
        elif location.wall_id < self.topology.walls_per_hex:
            location.page_id = 1
            location.book_id = 1
            location.shelve_id = 1
            location.wall_id += 1
        elif self.hex_conversion.decode(location.hex_id) < self.no_of_hexes.value:
            location.page_id = 1
            location.book_id = 1
            location.shelve_id = 1
            location.wall_id = 1
            location.hex_id = self.hex_conversion.encode(
                self.hex_conversion.decode(location.hex_id) + 1
            )
        else:
            location.page_id = 1
            location.book_id = 1
            location.shelve_id = 1
            location.wall_id = 1
            location.hex_id = "0"
        return location

    def previous(self, location: Location) -> Location:
        if location.page_id > 1:
            location.page_id -= 1
        elif location.book_id > 1:
            location.page_id = self.topology.pages_per_book
            location.book_id -= 1
        elif location.shelve_id > 1:
            location.page_id = self.topology.pages_per_book
            location.book_id = self.topology.books_per_shelve
            location.shelve_id -= 1
        elif location.wall_id > 1:
            location.page_id = self.topology.pages_per_book
            location.book_id = self.topology.books_per_shelve
            location.shelve_id = self.topology.shelves_per_wall
            location.wall_id -= 1
        elif self.hex_conversion.decode(location.hex_id) > 0:
            location.page_id = self.topology.pages_per_book
            location.book_id = self.topology.books_per_shelve
            location.shelve_id = self.topology.shelves_per_wall
            location.wall_id = self.topology.walls_per_hex
            location.hex_id = self.hex_conversion.encode(
                self.hex_conversion.decode(location.hex_id) - 1
            )
        else:
            location.page_id = self.topology.pages_per_book
            location.book_id = self.topology.books_per_shelve
            location.shelve_id = self.topology.shelves_per_wall
            location.wall_id = self.topology.walls_per_hex
            location.hex_id = self.hex_conversion.encode(self.no_of_hexes)
        return location

    def get_page_content(self, location: Location) -> Tuple[str, str]:
        text = self.get_text_from_location(location)
        stamp = self.get_stamp(location)
        return text, stamp

    def normalise_text(self, text: str) -> str:
        normalise_text = ""
        for char in text:
            if char in self.alphabet:
                normalise_text += char
        return normalise_text

    def get_location_from_user(self) -> Location:
        hex_id = self.get_user_input(self.browse_menu_hex_text, "str", 3003)
        wall_id = self.get_user_input(self.browse_menu_wall_text, "int", 4)
        shelve_id = self.get_user_input(self.browse_menu_shelve_text, "int", 5)
        book_id = self.get_user_input(self.browse_menu_book_text, "int", 32)
        page_id = self.get_user_input(self.browse_menu_page_text, "int", 410)
        location = Location(
            hex_id=str(hex_id),
            wall_id=int(str(wall_id)),
            shelve_id=int(str(shelve_id)),
            book_id=int(str(book_id)),
            page_id=int(str(page_id)),
        )
        return location

    def get_text_from_location(self, location: Location) -> str:
        page_location = (
            (self.hex_conversion.decode(location.hex_id) * self.topology.pages_per_hex)
            + ((location.wall_id - 1) * self.topology.pages_per_wall)
            + ((location.shelve_id - 1) * self.topology.pages_per_shelve)
            + ((location.book_id - 1) * self.topology.pages_per_book)
            + (location.page_id - 1)
        )
        return self.conversion.encode(page_location)

    def get_location_from_text(self, text: str) -> Location:
        location = self.conversion.decode(text)
        hex_id = Size(
            value=location // self.topology.pages_per_hex,
            remainder=location % self.topology.pages_per_hex,
            div=self.topology.pages_per_hex,
        )
        wall_id = Size(
            value=hex_id.remainder // self.topology.pages_per_wall + 1,
            remainder=hex_id.remainder % self.topology.pages_per_wall,
            div=self.topology.pages_per_wall,
        )
        shelve_id = Size(
            value=wall_id.remainder // self.topology.pages_per_shelve + 1,
            remainder=wall_id.remainder % self.topology.pages_per_shelve,
            div=self.topology.pages_per_shelve,
        )
        book_id = Size(
            value=shelve_id.remainder // self.topology.pages_per_book + 1,
            remainder=shelve_id.remainder % self.topology.pages_per_book,
            div=self.topology.pages_per_book,
        )
        page_id = Size(value=book_id.remainder + 1, remainder=0, div=1)
        hex_id = self.hex_conversion.encode(hex_id.value)
        return Location(
            hex_id=hex_id,
            wall_id=int(str(wall_id)),
            shelve_id=int(str(shelve_id)),
            book_id=int(str(book_id)),
            page_id=int(str(page_id)),
        )

    def get_user_input(self, text: str, value_type: str = "int", bound: int = 0) -> str:
        while True:
            user_input = input(text)
            user_input = self.test_type(user_input, value_type)
            user_bound = user_input if value_type == "int" else len(user_input)
            if self.test_bound(user_bound, bound):
                return user_input

    @staticmethod
    def clear_screen():
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def get_stamp(location: Location) -> str:
        return (
            f"{location.hex_id[:10]}-w{location.wall_id}-"
            f"s{location.shelve_id}-b{location.book_id}-p{location.page_id}"
        )

    @staticmethod
    def test_type(value: str, value_type: str = "int") -> bool:
        if value_type == "int":
            try:
                return int(value)
            except TypeError as e:
                print(e)
                return False
        if value_type == "str":
            return value.lower()
        else:
            raise ValueError()

    @staticmethod
    def test_bound(value: int, bound: int) -> bool:
        try:
            assert 1 <= value <= bound
        except AssertionError as e:
            print(e)
            return False
        return True

    @staticmethod
    def save_result(result: str, stamp: str) -> None:
        with open(stamp + ".txt", "w") as f:
            f.write(result)

    def __repr__(self) -> str:
        return (
            f"topology: {self.topology}\nno_of_pages: {self.no_of_pages}\n"
            f"no_of_books: {self.no_of_books}\nno_of_shelves: {self.no_of_shelves}\n"
            f"no_of_walls: {self.no_of_walls}\nno_of_hexes: {self.no_of_hexes}"
        )


if __name__ == "__main__":
    library = Library()
    library.run()
