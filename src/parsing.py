input_f=open("asm.in")
output_f=open("asm.out","w")

main_instructions= []
data= []
jump_counter= 0

def parse_and_transform(input_f, output_f):
    global main_instructions, data
    output_lines=[]
    input_lines = input_f.readlines()
    #gasesc unde incepe main
    main_index=-1
    for i,line in enumerate(input_lines):
        if "main:" in line:
            main_index=i
            break
    if main_index == -1:
        print("no main found")

    for i in range(main_index):
        line = input_lines[i].rstrip()
        output_lines.append(line)

    output_lines.append(".data")
    output_lines.extend(data)  #pt tabele
    output_lines.append("")
    output_lines.append(".text")
    output_lines.append(".global main")
    output_lines.append("main:")

    for i in range(main_index+1, len(input_lines)):
        line=input_lines[i].strip()

        if not line:
            output_lines.append("")
            continue

        transformed=process_instruction(line)
        output_lines.extend(transformed)

    with open("asm.out", 'w') as f:
        for line in output_lines:
            f.write(line + '\n')

def process_instruction(line):
    parts = line.split(None, 1)
    #impart linia in 2 parti: instructiune, operanzi/operand

    if not parts:
        return [line]

    return parse_parts(parts, line)





def parse_parts(parts, line):

    instruction = parts[0]
    operands_str = parts[1] if len(parts) > 1 else ""

    if instruction.startswith("mov"): #daca e mov, lasa asa (merge si pt movl, movb,...)
        return ["   "+line]

    elif instruction.startswith("add"):
        operands=parse_operands(operands_str)
        if len(operands) == 2:
            return transform_add(operands[0], operands[1])
        #to do: functia in sine de tranform_add
        #functia trb sa returneze o lista de linii
        else:
            return ["   "+line] #daca e altceva gresit, sare

    elif instruction.startswith("sub"):
        operands=parse_operands(operands_str)
        if len(operands) == 2:
            return transform_sub(operands[0], operands[1])
        else:
            return ["   "+line]

    elif instruction.startswith("mul"):
        operands=parse_operands(operands_str)
        if len(operands) == 2:
            return transform_mul(operands[0], operands[1])
        else:
            return ["   "+line]

    elif instruction.startswith("xor"):
        operands = parse_operands(operands_str)
        if len(operands) == 2:
            return transform_xor(operands[0], operands[1])
        else:
            return ["   " + line]

    elif instruction.startswith("or"):
        operands = parse_operands(operands_str)
        if len(operands) == 2:
            return transform_or(operands[0], operands[1])
        else:
            return ["   " + line]

    elif instruction.startswith("and"):
        operands = parse_operands(operands_str)
        if len(operands) == 2:
            return transform_and(operands[0], operands[1])
        else:
            return ["   " + line]

    elif instruction.startswith("dec"):
        operand = parse_operands(operands_str)
        if isinstance(operand, str):
            return transform_sub(operand , "$1")
        else:
            return ["   " + line]

    elif instruction.startswith("inc"):
        operand = parse_operands(operands_str)
        if isinstance(operand, str):
            return transform_add(operand, "$1")
        else:
            return ["   " + line]

    elif instruction.startswith("cmp"):
        operands= parse_operands(operands_str)
        if len(operands) == 2:
            return transform_cmp(operands[0], operands[1])
        else:
            return ["   " + line]

    elif instruction in ["je", "jge", "jg", "jl", "jle", "jne"]:
        target= operands_str.strip()
        return transform_jump(instruction, target)


    elif instruction=="jmp":
        target=operands_str.strip()
        return transform_jmp(target) #nu e dependent de un cmp


    elif instruction.startswith("lea"):
        operands = parse_operands(operands_str) #lea    v, %edi -> movl $v, %edi
        if len(operands) == 2:
            return tranform_lea(operands[0], operands[1])
        else:
            return ["   " + line]

    elif instruction.startswith("shl"):
        operands = parse_operands(operands_str)
        if len(operands) == 2:
            # shl $n, %registru=mul $(2 la n), %registru

            target = operands[1]

            if operands[0].startswith("$"):
                try:
                    n=int(operands[0][1:])
                    result=[]
                    while n>0:
                        result.extend( tranform_mul(operands[1], "$2"))
                        n=n-1
                    return result
                except:
                    return ["   " + line]
            else:
                return ["   " + line]
        else:
            return ["   " + line]

    #shr cred ca e imposibil, e cu div

        
    else:
        return ["   " + line] #daca am vreo instructiune unknown




def parse_operands(operands):
    if "," in operands:
        operands = operands.split(", ")
        return operands
    else:
        operand=operands
        return operand





def tranform_lea(operand1, operand2):
    operand1="$"+operand1
    lines=[]
    lines.append("mov "+operand1+" "+operand2)
    return lines




