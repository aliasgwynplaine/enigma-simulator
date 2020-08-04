#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import sys
import string
import random
from enigma import enigma, ALPH

BlackColor = '\u001b[30m'
RedColor = '\u001b[31m'
GreenColor = '\u001b[32m'
YellowColor = '\u001b[33m'
BlueColor = '\u001b[34m'
MagentaColor = '\u001b[35m'
CyanColor = '\u001b[36m'
WhiteColor = '\u001b[37m'
ResetColor = '\u001b[0m'


def menu():
    parser = argparse.ArgumentParser(description='Enigma machine')

    parser.add_argument(
        '-t', '--plaintext', help='text to encrypt or decrypt', type=str,
        required= True, dest='plaintext'
    )
    parser.add_argument(
        '-rd', '--radomize-plugboard', action='store_true',
        help='Randomize plugboard',
        dest='random_plugboard'
    )
    parser.add_argument(
        '-k', '--key', help='set key', dest='key', required=True
    )
    parser.add_argument(
        '-R', '--reflector', choices=['B', 'C'], help='set reflector type',
        default='B', dest='reflector'
    )
    parser.add_argument(
        '-r', '--rotors', nargs='+',
        help='list of rotors, choose 3 or more rotors and write them '
        'separated by spaces.', choices=['I', 'II', 'III', 'IV', 'V'],
        default=['I', 'II', 'III'],
        dest='rotors'
    )
    parser.add_argument(
        '-p', '--plugboard', nargs='*',
        help='optional plugboard conections. Example: AB CD XT',
        dest='plugboard'
    )
    parser.add_argument(
        '-v', '--verbose', help='set verbose mode on',
        action='store_true', dest='verbose'
    )

    args = parser.parse_args()

    #Check if plugboard option is not selected
    if args.plugboard != None :

        #Only 10 conections are allowed
        if len(args.plugboard)  > 10 :
            exit(
                RedColor +"[!] Error: Too many connections for the "
                "plugboard. Only 10 allowed"+ ResetColor
            )

        plugboard = args.plugboard
        tmp = []

        #Check if each letter has a corresponding one
        for p in plugboard :
            if len(p) != 2 :
                exit(
                    RedColor +"[!] Error: Bad plugboardboard parameters"+
                    ResetColor
                )
        pass

    else:
        plugboard = None

    #Check if the parameter random is ON
    if args.random_plugboard :
        print(MagentaColor +"[!] Random plugboard option: ON"+ ResetColor)
        shuffle_list = list(ALPH)
        random.shuffle(shuffle_list)    
        plugboard = list(
            map(lambda t: t[0]+t[1], zip(shuffle_list[:10], shuffle_list[10:20]))
        )

    if args.key is None :
        sys.stderr.write(RedColor +'[!] You must enter a key\n'+ ResetColor)
        exit(1)

    #Check length of the key
    if len(args.key) != len(args.rotors) :
        exit(
            RedColor +"[!] Error: key length is different from "
            "the number of rotors selected"+ ResetColor
        )

    return (
        args.plaintext, args.key, args.rotors, 
        args.reflector, args.plugboard, args.verbose
    )



if __name__ == "__main__" :
    text, key, rotors, reflector, plugboard, v = menu()
    instance = enigma(rotors, reflector, key=key, plugboard=plugboard)
    instance.setkey(key)
    crypt = instance.run(text)

    if v :

        print (GreenColor +"""
        __.....__         _..._    .--.             __  __   ___               
    .-''         '.     .'     '.  |__|   .--./)   |  |/  `.'   `.             
   /     .-''"'-.  `.  .   .-.   . .--.  /.''\\    |   .-.  .-.   '            
  /     /________\   \ |  '   '  | |  | | |  | |   |  |  |  |  |  |     __     
  |                  | |  |   |  | |  |  \`-' /    |  |  |  |  |  |  .:--.'.   
  \    .-------------' |  |   |  | |  |  /("'`     |  |  |  |  |  | / |   \ |  
   \    '-.____...---. |  |   |  | |  |  \ '---.   |  |  |  |  |  | `" __ | |  
    `.             .'  |  |   |  | |__|   /'""'.\  |__|  |__|  |__|  .'.''| |  
      `''-...... -'    |  |   |  |       ||     ||                  / /   | |_ 
                       |  |   |  |       \'. __//                   \ \._,\ '/ 
                       '--'   '--'        `'---'                     `--'  `"  
                                                              simulator
        """+ ResetColor)


        print(CyanColor +"[*] Plugboard:\t"+ ResetColor, end='')

        if instance.getPlugboard() is None :
            print(instance.getPlugboard())

        else :
            for p in instance.getPlugboard() :
                print(p[0]+p[1], end=' ')

            print()

        print(CyanColor +"[*] Rotors:\t"+ ResetColor, end='')

        for r in rotors :
            print(r, end=' ')

        print()
        print(CyanColor +"[*] Reflector:\t"+ ResetColor + reflector)
        print(CyanColor +"[*] Key:\t"+ ResetColor + key)
        print()
        print(YellowColor + "[>] Result:\t" + crypt + ResetColor)
        print()
    
    else :
        print(crypt)
