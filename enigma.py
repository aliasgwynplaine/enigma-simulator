#!/usr/bin/python3
# -*- coding: utf-8 -*-
# import os
import sys
import string

ALPH = string.ascii_uppercase
FORWARD = 1
BACKWARD = 0

"""
Shitty enigma api.
Read this in order to understand
http://users.telenet.be/d.rijmenants/en/enigmatech.htm#top

Entry = ABCDEFGHIJKLMNOPQRSTUVWXYZ (rotor right side)
        ||||||||||||||||||||||||||
I     = EKMFLGDQVZNTOWYHXUSPAIBRCJ
II    = AJDKSIRUXBLHWTMCQGZNPYFVOE
III   = BDFHJLCPRTXVZNYEIWGAKMUSQO
IV    = ESOVPZJAYQUIRHXLNFTGKDCMWB
V     = VZBRGITYUPSDNHLXAWMJQOFECK


Contacts    = ABCDEFGHIJKLMNOPQRSTUVWXYZ
              ||||||||||||||||||||||||||
Reflector B = YRUHQSLDPXNGOKMIEBFZCWVJAT
Reflector C = FVPJIAOYEDRZXWGCTKUQSBNMHL

A => 0   F => 5   K => 10   P => 15   U => 20   Z => 25
B => 1   G => 6   L => 11   Q => 16   V => 21
C => 2   H => 7   M => 12   R => 17   W => 22
D => 3   I => 8   N => 13   S => 18   X => 23
E => 4   J => 9   O => 14   T => 19   Y => 24
"""

TYPE_I = ([_ for _ in zip(ALPH, 'EKMFLGDQVZNTOWYHXUSPAIBRCJ')], 16) # notch: Q ~ 16
TYPE_II = ([_ for _ in zip(ALPH, 'AJDKSIRUXBLHWTMCQGZNPYFVOE')], 4) # notch: E ~ 4
TYPE_III = ([_ for _ in zip(ALPH, 'BDFHJLCPRTXVZNYEIWGAKMUSQO')], 21) # notch: V ~ 21
TYPE_IV = ([_ for _ in zip(ALPH, 'ESOVPZJAYQUIRHXLNFTGKDCMWB')], 9) # notch: J ~ 9
TYPE_V = ([_ for _ in zip(ALPH, 'ESOVPZJAYQUIRHXLNFTGKDCMWB')], 25)# notch: Z ~ 25
REFLECTOR_B = ([_ for _ in zip(ALPH, 'YRUHQSLDPXNGOKMIEBFZCWVJAT')], -1)
REFLECTOR_C = ([_ for _ in zip(ALPH, 'FVPJIAOYEDRZXWGCTKUQSBNMHL')], -1 )



def create_mapping(lmap) :
    """creates a mapping, in the form of a list of tuples, from a given 
    permutation of the alphabet by zipping it."""
    foreigncharfound = True in map(lambda c: c not in ALPH, lmap)

    if len(set(lmap)) != 26 or foreigncharfound:
        sys.stderr.write('Check your permutation.\n')
        exit(-1)

    return [_ for _ in zip(ALPH, lmap)]

class reflector : 
    """we will consider B and C reflektors"""
    # todo

class rotor :
    """The rotor"""
    def __init__(self, name= 'I', config=TYPE_I, ring= 0) :
        self._set_config(name, config, ring)

    def __str__(self) :
        pass

    def _set_config(self, name= 'I', config=TYPE_I, ring= 0) :
        self.name = name

        if len(config[0]) != 26 :
            sys.stderr.write("Wrong mapping. Requires 26 len.\n")
            exit(1)

        self.mapping = config[0]
        self.mapping_inv = [(_[1],_[0]) for _ in config[0]]
        self.mapping_inv.sort()
        self.ring = ring
        self.pos = 0
        self.notch = config[1]



    def sym_right(self, pos) :
        """use this function when inputing a symbol from the right"""
        relative_pos = (self.pos + pos ) % 26
        ret_let = self.mapping[relative_pos][1]
        rel_ret_pos = ord(ret_let) - 65
        ret_pos = (rel_ret_pos - self.pos) % 26

        return ret_pos


    def sym_left(self, pos) :
        """use this function when inputing a symbol from the left"""
        relative_pos = (self.pos + pos ) % 26
        ret_let = self.mapping_inv[relative_pos][1]
        rel_ret_pos = ord(ret_let) - 65
        ret_pos = (rel_ret_pos - self.pos) % 26

        return ret_pos


    def _rot(self, step= FORWARD, force= False) :
        """rot forwards or backwards without inputing a shit
        Returns True if notch is touched, False otherwise."""
        retval = False

        if step == FORWARD :
            retval = self.notch == self.pos

            if retval or force :
                self.pos = (self.pos + 1) % 26
        else : 
            self.pos = (self.pos - 1) % 26

        return retval


    def setkeyletter(self, lett) :
        self.pos = ALPH.find(lett)

    def set_pos(self, pos) :
        if pos < 27 and pos >= 0 :
            self.pos = pos
        else :
            sys.stderr.write(
                'Invalid position!\n'
            )
            exit(1)


    def getpos(self) :
        """Returns actual position"""
        return self.pos


class enigma :
    """This shitty class is suposed to be the machine"""
    def __init__(
        self,order_rotor= ['I', 'II', 'III'], 
        reflector_type= 'B',
        key= 'KEY',
        plugboard=None
    ) :
        self.rots = []

        for o in order_rotor:
            if o == 'I':
                self.rots.append(rotor('I', TYPE_I))
            elif o == 'II':
                self.rots.append(rotor('II', TYPE_II))
            elif o == 'III':
                self.rots.append(rotor('III', TYPE_III))
            elif o == 'IV':
                self.rots.append(rotor('IV', TYPE_IV))
            elif o == 'V':
                self.rots.append(rotor('V', TYPE_V))
            else:
                sys.stderr.write(
                    "Wrong selected rotor type. Choose one of theese "
                    "options (I, II, III, IV, V).\n"
                )
                exit(1)

        self.set_reflector(reflector_type)

        self.setkey(key)
        self.lastkeysetted = key
        self.plugboard = None

        self._set_plugboard(plugboard)


    def reset(self) :
        """todo: Just in case we have config file or..."""


    def set_reflector(self, reflector_type='B') :
        if reflector_type == "B":
            self.reflector = rotor('B', REFLECTOR_B)
        elif reflector_type == "C":
            self.reflector = rotor('C', REFLECTOR_C)


    def _addrotor(self, rot) :
        """adds a new rotor.
        This method returns a reference to the added rotor."""
        if len(self.rots) <= 10 :
            self.rots.append(rot)
            return rot
        else :
            sys.stderr.write('You cannot add more rotors\n')
            return None


    def _remove_rotor(self, index) :
        """removes rotor in index. Returns 0 if removed, 1 otherwise.
        Cannot remove less than 3 rotors."""
        if len(self.rots) <= 3 :
            sys.stderr.write(
                'Cannot have less than 3 rotors.\n'
            )
            return 1
        else :
            self.rots.remove(self.rots[index])
            return 0


    def _set_plugboard(self, pluglist) : # list pairs of letters
        """set the plugboard. pluglist must be passed as a list
        of pairs of letters. For example ['AB', 'CD', 'XZ'].
        Returns 0 if success, 1 if some letter is repeated and 2 
        if a non pair is passed."""
        if pluglist is None or pluglist == [''] :
            self.plugboard = None
        else :  
            plugstr = ''.join(pluglist)

            if len(plugstr) != len(set(plugstr)) :
                sys.stderr.write(
                    'Wrong plugboard\n'
                )
                sys.stdout.write(
                    'Using plugboard: {}\n'.format(self.plugboard)
                )
                return 1

            tmp = []

            for pluginput in pluglist :
                if len(pluginput) != 2 :
                    sys.stderr.write(
                        "Error: Bad plugboardboard parameters\n"
                    )
                    return 2
                tmp.append((pluginput[0], pluginput[1]))
            
            self.plugboard = tmp
        return 0


    def getrots(self) :
        """Returns the list of rotors"""
        return self.rots

    
    def getPlugboard(self) :
        """returns the plugboard"""
        return self.plugboard

    
    def getReflector(self) :
        """returns reflector"""
        return self.reflector


    def setkey(self, key) :
        """Set key in rotors from left to right"""
        if len(key) != len(self.rots) :
            sys.stderr.write(
                "Key length is different from "
                "the number of rotors selected\n"
            )
            exit(1)

        for r,k in zip(self.rots, key) :
            r.setkeyletter(k)

        self.lastkeysetted = key

    def swap(self, x) :
        """swapps letter x in plugboard"""
        if self.plugboard != None :
            for p in self.plugboard:
                if x == p[0]:
                    return p[1]
                elif x == p[1]:
                    return p[0]
        return x

    def _rotate_rotors(self) :
        carry = True

        for rotor in reversed(self.rots) : # Mateus 20:16
            carry = rotor._rot(force= carry)

    def step(self, mylet, ignore= True) :
        """performs just one step"""
        pos = ALPH.find(mylet)

        if pos!=-1:
            pos = ALPH.find(self.swap(mylet)) # swap letter with plugboard
            self._rotate_rotors()

            for myrotor in reversed(self.rots) :
                pos = myrotor.sym_right(pos)

            pos = self.reflector.sym_right(pos)

            for myrotor in self.rots :
                pos = myrotor.sym_left(pos)

            return self.swap(ALPH[pos]) #swap letter with plugboard

        if ignore :
            return # None

        return mylet


    def run(self, myinput, ignore= True) :
        """to decrypt and to encrypt"""
        myinput = myinput.upper()
        ciphertext = []
        count = 0

        for sym in myinput :
            cryptolet = self.step(sym)

            if not cryptolet is None :
                count = (count + 1) % 5
                ciphertext.append(cryptolet)

                if not count :
                    ciphertext.append(' ')

        return ''.join(ciphertext)

