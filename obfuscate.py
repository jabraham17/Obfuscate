
import sys
import os
import argparse as ap
from typing import Callable, Dict, List, Tuple
import re


class Obfuscators_x64:

    @staticmethod
    def getLabel():
        if not hasattr(Obfuscators_x64.getLabel, "currentCount"):
            Obfuscators_x64.getLabel.currentCount = 0
        label = f".LobsGenLabel{Obfuscators_x64.getLabel.currentCount}"
        Obfuscators_x64.getLabel.currentCount+=1
        return label


    @staticmethod
    def PushAndJump(call_name: str) -> List[str]:
        """
        PushAndJump

        extern hello
        main:
            push r10 ; save register we are going to use, we can mess this up according to calling convention
            mov r10, hello ; move label to register for call
            jmp 0x5 ; jmp over extra byte
            db 0xe9 ; extra byte, tells assembler this is a jmp
            call r10 ; is 3 bytes long beacuse we use an extended register, completely hidden in jmp imm
            pop r10 ; shows up as pop rdx, as the first byte gets included in the jmp imm

        """


        output = []
        #output.append("push r10")
        output.append(f"mov r10, qword ptr [rip + {call_name}]")
        label = Obfuscators_x64.getLabel()
        output.append(f"jmp {label}")
        output.append(".byte 0xe9")
        output.append(f"{label}: call r10")
       # output.append("pop r10")
        output = list([str(o + "\n") for o in output])
        return output


Obfuscators_x64.mapping = {
    "PushAndJump": Obfuscators_x64.PushAndJump
}


def load_dictionary(file: str, default_method: str) -> Dict[str, str]:
    """load a dictionary of which calls to replace and how"""
    calls = dict()
    lines = []
    with open(file, "r") as f:
        # read all lines with content
        lines = [l.strip() for l in f.readlines() if l.strip() != ""]
    for line in lines:
        if line.startswith("//"):
            continue
        components = [c.strip() for c in line.split("->") if c.strip() != ""]
        if len(components) == 1:
            calls[components[0]] = default_method
        elif len(components) == 2:
            calls[components[0]] = components[1]
    return calls

def construct_call_regex(calls_dict: Dict[str, str]) -> str:
    base = r"call.*?"
    call_groups = [f"(?:{call_name})" for call_name in calls_dict.keys()]
    call_group = "|".join(call_groups)
    regex = base + f"({call_group})"
    return regex



def identifyAndReplace(input_lines: List[str], calls_dict: Dict[str, str]):
    regex = re.compile(construct_call_regex(calls_dict))
    replacements: List[Tuple[int, List[str]]] = []
    for idx, l in enumerate(input_lines):
        if m:= re.search(regex, l):
            call_name = m[1]
            method = None
            for k, v in calls_dict.items():
                if re.match(k, call_name):
                    method = v
                    break
            func = Obfuscators_x64.mapping.get(method, None)
            if func:
                replacement = func(call_name)
                replacements.append((idx, replacement))
    for idx, replacement in reversed(replacements):
        input_lines[idx:idx+1] = replacement
    return input_lines




def cli_args():
    p = ap.ArgumentParser("obfuscate assembly on windows")
    p.add_argument("file", help="input file")
    p.add_argument("--method", "-m", choices=["PushAndJump", "MoveAndOverwrite", "ObscureAVX512"], default="PushAndJump", help="default obscure method to use")
    p.add_argument("-o", "--output", help="output file name")
    p.add_argument("-c", "--call-dictionary", help="dictionary file for calls to replace")

    args = p.parse_args()
    root_dir = os.getcwd()
    args.file = os.path.join(root_dir, args.file)
    args.call_dictionary = os.path.join(root_dir, args.call_dictionary)
    if not args.output:
        basename, ext = os.path.splitext(args.file)
        args.output = basename + ".obs" + ext
    return args

def main():
    args = cli_args()

    calls_dict = load_dictionary(args.call_dictionary, args.method)
    lines = open(args.file, "r").readlines()
    output_lines = identifyAndReplace(lines, calls_dict)
    with open(args.output, "w") as f:
        f.writelines(output_lines)

if __name__ == "__main__":
    main()

