input_f = open("asm.in")
output_f = open("asm.out", "w")

main_instructions = []
data = []
jump_counter = 0

def parse_and_transform(input_f, output_f):
    global main_instructions, data
    output_lines = []
    input_lines = input_f.readlines()
    # gasesc unde incepe main
    main_index = -1
    data_start = -1
    for index, line in enumerate(input_lines):
        if ".data" in line:
            data_start = index
        if "main:" in line:
            main_index = index
            break
    if main_index == -1:
        print("no main found")
        return

    if data_start != -1:
        for i in range(data_start + 1, main_index):
            line = input_lines[i].strip()
            if line and not line.startswith('.text') and not line.startswith('.global'):
                output_lines.append(line)

    processed_instructions = []
    for i in range(main_index + 1, len(input_lines)):
        line = input_lines[i].strip()
        if not line:
            processed_instructions.append("")
            continue
        transformed=process_instruction(line)
        if isinstance(transformed, tuple):
            transformed = transformed[0]
        processed_instructions.extend(transformed)

    data = set(data)
    output_lines_final = []
    output_lines_final.append(".data")
    output_lines_final.extend(output_lines)
    output_lines_final.extend(data)
    output_lines_final.append("")
    output_lines_final.append(".text")
    output_lines_final.append(".global main")
    output_lines_final.append("main:")
    output_lines_final.extend(processed_instructions)

    for line in output_lines_final:
        if line.strip() and not line.strip().endswith(':') and not line.startswith('.'):
            output_f.write('\t' + line + '\n')
        else:
            output_f.write(line + '\n')


def process_instruction(line):
    parts = line.split(None, 1)
    # impart linia in 2 parti: instructiune, operanzi/operand

    if not parts:
        return [line]

    return parse_parts(parts, line)


def parse_parts(parts, line):
    instruction = parts[0]
    operands_str = parts[1] if len(parts) > 1 else ""
    global main_instructions

    if instruction.startswith("mov"):  # daca e mov, lasa asa (merge si pt movl, movb,...)
        return [line]

    elif instruction.startswith("add"):
        operands = parse_operands(operands_str)
        if len(operands) == 2:
            lines, data_nou = transform_add(operands[0], operands[1])
            data.extend(data_nou)
            return lines
        # to do: functia in sine de tranform_add
        # functia trb sa returneze o lista de linii
        else:
            return [line]  # daca e altceva gresit, sare

    elif instruction.startswith("sub"):
        operands = parse_operands(operands_str)
        if len(operands) == 2:
            return transform_sub(operands[0], operands[1])
        else:
            return [line]


    elif instruction.startswith("mul"):
        operands = parse_operands(operands_str)
        if len(operands) == 2:
            return transform_mul(operands[0], operands[1])
        else:
            return [line]

    elif instruction.startswith("xor"):
        operands = parse_operands(operands_str)
        if len(operands) == 2:
            return transform_xor(operands[0], operands[1])
        else:
            return [line]

    elif instruction.startswith("or"):
        operands = parse_operands(operands_str)
        if len(operands) == 2:
            return transform_or(operands[0], operands[1])
        else:
            return [line]

    elif instruction.startswith("and"):
        operands = parse_operands(operands_str)
        if len(operands) == 2:
            return transform_and(operands[0], operands[1])
        else:
            return [line]

    elif instruction.startswith("not"):
        operand = parse_operands(operands_str)
        if len(operand) == 1:
            return transform_not(operand)
        else:
            return [line]

    elif instruction.startswith("dec"):
        operand = parse_operands(operands_str)
        if isinstance(operand, str):
            L=["mov $1, %eax"]
            L.extend(transform_sub("%eax", operand)[0])
            return L
        else:
            return [line]

    elif instruction.startswith("inc"):
        operand = parse_operands(operands_str)
        if isinstance(operand, str):
            L=["mov $1, %eax"]
            L.extend(transform_add("eax", operand)[0])
            return L
        else:
            return [line]

    elif instruction.startswith("cmp"):
        operand = parse_operands(operands_str)
        if len(operand) == 2:
            return transform_cmp(operand[0], operand[1])
        else:
            return [line], []

    elif instruction in ["je", "jge", "jg", "jl", "jle", "jne"]:
        target = operands_str.strip()
        return transform_conditional_jump(instruction, target)


    elif instruction == "jmp":
        target = operands_str.strip()
        return transform_unconditional_jump(target)  # nu e dependent de un cmp

    elif instruction == "loop":
        target = operands_str.strip()
        return transform_loop_instr(target)


    elif instruction.startswith("lea"):
        operands = parse_operands(operands_str)  # lea    v, %edi -> movl $v, %edi
        if len(operands) == 2:
            return tranform_lea(operands[0], operands[1])
        else:
            return [line]

    # elif instruction.startswith("shl"):
    #     operands = parse_operands(operands_str)
    #     if len(operands) == 2:
    #         # shl $n, %registru=mul $(2 la n), %registru
    #
    #         target = operands[1]
    #
    #         if operands[0].startswith("$"):
    #             try:
    #                 n=int(operands[0][1:])
    #                 result=[]
    #                 while n>0:
    #                     result.extend( tranform_mul(operands[1], "$2"))
    #                     n=n-1
    #                 return result
    #             except:
    #                 return [line]
    #         else:
    #             return [line]
    #     else:
    #         return [line]
    #
    # #shr cred ca e imposibil, e cu div
    #
    #

    elif instruction.startswith("push"):
        if "," in operands_str:
            return [line]
        else:
            operand=parse_operands(operands_str)
            instrs= []
            sub_instr, sub_data= transform_sub("$4", "%esp")
            data.extend(sub_data)
            instrs.extend(sub_instr)
            instrs.append(f"mov {operand}, 0(%esp)")
            return instrs



    elif instruction.startswith("pop"):
        if "," in operands_str:
            return [line]

        else:
            operand = parse_operands(operands_str)
            instrs=[]
            instrs.append(f"mov 0(%esp), {operand}")
            add_instr, add_data=transform_add("$4", "%esp")
            data.extend(add_data)
            instrs.extend(add_instr)
            instrs.append("movl rez, %esp")
            return instrs



    else:
        return [line]  # daca am vreo instructiune unknown


def parse_operands(operands):
    if "," in operands:
        operands = operands.split(", ")
        return operands
    else:
        operand = operands
        return operand


def tranform_lea(operand1, operand2):
    operand1 = "$" + operand1
    lines = []
    lines.append("mov " + operand1 + " " + operand2)
    return lines


def transform_add(first_operand, second_operand):
    main_instructions = []
    main_instructions.append("mov $0, old_carry")
    main_instructions.append(f"movl {first_operand}, first_temp_storage")  # punem operanzii in memorie pentru a ii putea extrage pe bytes
    main_instructions.append(f"movl {second_operand}, second_temp_storage")
    for index in range(4):
        main_instructions.append(f"mov first_temp_storage+{index}, %ah")  # daca punem in ah o sa fie 256*first_index_operand si accesarea tabelului va fi ok
        main_instructions.append(f"mov second_temp_storage+{index}, %al")  # aici va fi valoarea byteului din second operand
        # ah=rand, #al = coloana
        main_instructions.append(f"movzwl %ax, %esi")  # ax = ah+al => retinem in esi indexul corect; movzwl muta ax in esi si umple restul cu 0
        main_instructions.append(f"movb sum_table(%esi), %cl")  # retinem suma partiala tot intr-un registru de un byte
        main_instructions.append(f"movb carry_sum_table(%esi), %dl")  # retinem carry-ul
        main_instructions.append(f"movb %cl, %ah")  # mutam suma partiala in ah pentru a aduna carry-ul, daca exista
        main_instructions.append(f"movb old_carry, %al")  # daca old_carry=0 =>suma partiala va fi suma finala, altfel adaugam 1
        main_instructions.append(f"movzbl %ax, %esi")  # noul index, practic cauta pe coloanele 0 sau 1, in functie de old carry
        main_instructions.append(f"movb sum_table(%esi), %cl")  # suma finala
        main_instructions.append(f"mov carry_sum_table(%esi), %dh")  # al doilea carry
        main_instructions.append(f"movb %cl, rez+{index}")  # retinem in rezultat byte-ul calculat

        # calculam carry-ul final pentru urmatorul byte
        main_instructions.append("movb %dl, %ah")
        main_instructions.append("movb %dh, %al")
        main_instructions.append("movzbl %ax, %esi")
        main_instructions.append("movb or_table(%esi), %al")
        main_instructions.append("movb %al, old_carry")
    data_nou = ["rez: .space 4",
                "first_temp_storage: .space 4",
                "second_temp_storage: .space 4",
                "old_carry: .space 1"]
    return main_instructions, data_nou


def split_in_bytes(operand):
    local_instructions = []
    for index in range(4):
        local_instructions.append(f"movb {operand} + {index}, {operand}_{index}")
    return local_instructions


def multiplicate_by_256(operand):
    local_instructions = []
    local_instructions.append(f"movb sumation_table(zero_vaue, {operand}, 256), {operand}_times_256")
    return local_instructions


def create_choosing_table(first_operand, second_operand):
    local_data = []
    local_data.append("choosing_table: .long ")
    for index in range(5):
        data.append("0, ")
    local_data.append("0")
    main_instructions.append(f"mov {first_operand}, choosing_table")
    main_instructions.append(f"mov {second_operand}, choosing_table + 4")
    main_instructions.append(f"mov {first_operand}, choosing_table + 8")
    main_instructions.append(f"mov {second_operand}, choosing_table + 12")
    main_instructions.append(f"mov {second_operand}, choosing_table + 16")
    main_instructions.append(f"mov {first_operand}, choosing_table + 20")


def create_byte_comparison_table():
    total_data = [0, 1, 2, 1, 1, 1, 2, 2, 2]
    return total_data


def create_checking_table():
    total_data = []
    total_data.append("checking_table: .long ")
    total_data.append("0")
    total_data.append("0")
    return total_data


def transform_checking_table():
    local_instructions = []
    local_instructions.append("mov first_operand, checking_table(zero_value, one_value, 4)")
    return local_instructions


def transform_mul(first_operand, second_operand):
    local_instructions = []
    total_data = []

    instructions, cmp_data = transform_cmp(first_operand, second_operand)
    local_instructions.extend(instructions)
    total_data.extend(cmp_data)
    # totul este salvat in global_data

    local_instructions.extend(create_choosing_table(first_operand, second_operand))

    local_instructions.append("mov times_8(global_value, zero_value, 1), global_value_times_8")
    local_instructions.append("mov choosing_table(global_value_times_8, zero_value, 1), first_operand")
    local_instructions.append("mov $1, one_value")
    local_instructions.append("mov choosing_table(global_value_times_8, one_value, 4), second_operand")
    # pana aici in first_operand se afla valoarea mai mare si in second_operand valoarea mai mica

    number_of_repetitions = 32
    local_instructions.append("mov $1, checking_value")
    local_instructions.append("mov $0, total_sum")

    for index in range(number_of_repetitions):
        # trebuie facut and intre second_value si checking_value
        and_instructions = transform_and("second_operand", "checking_value")
        local_instructions.extend(and_instructions)
        # avem in acest moment o valoare care este 0 sau checking_value -> se poate duce pana la 2^32 => putem face o tabela doar cu puteri ale lui 2
        # presupunem ca avem resultatul intr o variabila result
        local_instructions.extend(transform_cmp("result", "zero_value"))
        # nu are cum sa fie mai mica decat 0 deci facem o tabela : 0, first_value
        total_data.extend(create_checking_table)
        local_instructions.extend(transform_checking_table)
        local_instructions.append("mov checking_table(zero_value, global_value, 4), and_result")

        new_instructions, new_data = transform_add("and_result, total_sum")
        local_instructions.extend(new_instructions)
        total_data.extend(new_data)

        new_instructions, new_data = transform_add("checking_value, checking_value")
        local_instructions.extend(new_instructions)
        total_data.extend(new_data)

        new_instructions, new_data = transform_add("first_operand, first_operand")
        local_instructions.extend(new_instructions)
        total_data.extend(new_data)
        # trebuie vazut in ce variabila se salveaza rezultatul adunarii

    local_instructions.append(f"{first_operand}, total_sum")
    return local_instructions, total_data


def transform_not(registru):
    main_instructions = []
    main_instructions.append(f"mov {registru}, operand")
    for index in range(4):
        main_instructions.append(f"movb operand + {index}, %al")
        main_instructions.append(f"movb %al, deplasament")
        main_instructions.append(f"movb deplasament(not_table), operand + {index}")
    main_instructions.append(f"mov operand, {registru}")
    new_data = ["not_table: .byte " + ",".join(str(255 - i) for i in range(256))]
    return main_instructions, new_data


def transform_and(first_operand, second_operand):
    local_instructions = []
    local_instructions.append(f"mov {first_operand}, first_and_storage")
    local_instructions.append(f"mov {second_operand}, second_and_storage")
    for i in range(4):
        local_instructions.append(f"movb first_and_storage+{i}, %ah")
        local_instructions.append(f"movb second_and_storage+{i}, %al")
        local_instructions.append(f"movzwl %ax, %esi")  # movzwl muta toti cei 16 biti in %esi si umple restul cu 0
        local_instructions.append(f"movb and_table(%esi), %cl")
        local_instructions.append(f"movb %cl, rez_and+{i}")
    data_nou = ["first_and_storage: .space 4", "second_and_storage: .space 4", "rez_and: .space 4"]
    return local_instructions, data_nou


def transform_or(first_operand, second_operand):
    local_instructions = []
    local_instructions.append(f"mov {first_operand}, first_or_storage")
    local_instructions.append(f"mov {second_operand}, second_or_storage")
    for i in range(4):
        local_instructions.append(f"movb first_or_storage+{i}, %ah")
        local_instructions.append(f"movb second_or_storage+{i}, %al")
        local_instructions.append(f"movzwl %ax, %esi")  # movzwl muta toti cei 16 biti in %esi si umple restul cu 0
        local_instructions.append(f"movb or_table(%esi), %cl")
        local_instructions.append(f"movb %cl, rez_or+{i}")
    data_nou = ["first_or_storage: .space 4", "second_or_storage: .space 4", "rez_or: .space 4"]
    return local_instructions, data_nou


def transform_xor(first_operand, second_operand):
    local_instructions = []
    local_instructions.append(f"mov {first_operand}, first_xor_storage")
    local_instructions.append(f"mov {second_operand}, second_xor_storage")
    for i in range(4):
        local_instructions.append(f"movb first_xor_storage+{i}, %ah")
        local_instructions.append(f"movb second_xor_storage+{i}, %al")
        local_instructions.append(f"movzwl %ax, %esi")  # movzwl muta toti cei 16 biti in %esi si umple restul cu 0
        local_instructions.append(f"movb xor_table(%esi), %cl")
        local_instructions.append(f"movb %cl, rez_xor+{i}")
    data_nou = ["first_xor_storage: .space 4", "second_xor_storage: .space 4", "rez_xor: .space 4"]
    return local_instructions, data_nou


def transform_cmp(first_operand, second_operand):
    local_instructions = []
    total_data = []

    local_instructions.append("mov $0, zero_value")
    local_instructions.extend(split_in_bytes(first_operand))
    local_instructions.extend(split_in_bytes(second_operand))
    local_instructions.extend(multiplicate_by_256(first_operand))

    new_data = create_byte_comparison_table()
    total_data.extend(new_data)

    local_instructions.append("mov comparison_table(first_operand_3_times_256, second_operand_3, 1), global_value")
    local_instructions.append("mov comparison_table(first_operand_2_times_256, second_operand_2, 1), local_value")
    local_instructions.append("mov times_3(global_value, zero_value, 1), global_value_times_3")
    local_instructions.append("mov byte_comparison_table(global_value_times_3, local_value, 1), global_value")
    local_instructions.append("mov comparison_table(first_operand_1_times_256, second_operand_1, 1), local_value")
    local_instructions.append("mov times_3(global_value, zero_value, 1), global_value_times_3")
    local_instructions.append("mov byte_comparison_table(global_values_time_3, local_value, 1), global_value")
    local_instructions.append("mov comparison_table(first_operand_0_times_256, second_operand_0, 1), local_value")
    local_instructions.append("mov times_3(global_value, zero_value, 1), global_value_times_3")
    local_instructions.append("mov byte_comparison_table(global_value_times_3, zero_value, 1), global_value")
    # daca global_value = 0, atunci numerele sunt egale, daca este egal cu 1, atunci first_operand e mai mare, daca e egal cu 2, second_operand e mai mare
    return local_instructions, total_data



def transform_sub(first_operand, second_operand):
    all_instructions = []
    total_data = []

    all_instructions.append(f"movl {first_operand}, sub_temp")
    total_data.append("sub_temp: .space 4")
    total_data.append("operand: .space 4")
    total_data.append("deplasament: .space 1")

    lines_not, data_not = transform_not("sub_temp")
    all_instructions.extend(lines_not)
    total_data.extend(data_not)

    lines_a1, data_a1 = transform_add(second_operand, "sub_temp")
    all_instructions.extend(lines_a1)
    total_data.extend(data_a1)

    lines_a2, data_a2 = transform_add("rez", "$1")
    all_instructions.extend(lines_a2)
    total_data.extend(data_a2)

    all_instructions.append(f"movl rez, {second_operand}")



    return all_instructions, total_data


def append_bytes_table(label, values):
    # transforma o lista de int-uri intro lista .byte
    lines = []
    lines.append(f"{label}:")
    size = 16
    for i in range(0, len(values), size):
        chunk = values[i: i + size]
        str_val = ", ".join(str(x) for x in chunk)
        lines.append(f"    .byte {str_val}")
    return lines


def get_cmp_tables():
    # generam tabelele cmp si transition o singura data
    global tables_generated
    if tables_generated:
        return []  # daca am generat deja, nu mai returnam nimic

    data_lines = []

    cmp_table = []
    for a in range(256):
        for b in range(256):
            if a == b:
                cmp_table.append(0)
            elif a > b:
                cmp_table.append(1)
            else:
                cmp_table.append(2)
    data_lines.extend(append_bytes_table("cmp_byte_table", cmp_table))

    transition_table = []
    for old in range(256):
        for new in range(256):
            if old == 0:
                transition_table.append(new)
            else:
                transition_table.append(old)
    data_lines.extend(append_bytes_table("transition_table", transition_table))

    tables_generated = True
    return data_lines


def transform_conditional_jump(jump_type, target_label):
    global jump_counter
    instr = []
    data_list = []
    jump_mask = [0, 0, 0]

    if jump_type == "je":
        jump_mask = [1, 0, 0]
    elif jump_type == "jne":
        jump_mask = [0, 1, 1]
    elif jump_type == "jg":
        jump_mask = [0, 1, 0]
    elif jump_type == "jge":
        jump_mask = [1, 1, 0]
    elif jump_type == "jl":
        jump_mask = [0, 0, 1]
    elif jump_type == "jle":
        jump_mask = [1, 0, 1]

    mask_name = f"mask_table_{jump_counter}"
    data_list.append(f"{mask_name}: .byte , {jump_mask[1]}, {jump_mask[2]}")

    instr.append(f"mov $0, %edx")
    instr.append(f"mov comparison_state, %dl")
    instr.append(f"movb {mask_name}(%edx), %al")  # al=1 daca trb sa sarim, 0 altfel
    next_label = f"next_{jump_counter}"
    choosing_name = f"jump_targets_{jump_counter}"
    data_list.append(f"{choosing_name}:")
    data_list.append(f"    .long {next_label}")
    data_list.append(f"    .long {target_label}")

    instr.append("movl $0, %ecx")
    instr.append("movb %al, %cl")
    instr.append(f"mov {choosing_name}(, %ecx, 4), %ebx")
    instr.append("mov %ebx, (%esp)")
    instr.append("ret")
    instr.append(f"{next_label}:")
    jump_counter += 1
    return instr, data_list


def transform_unconditional_jump(target_label):
    instr = []
    instr.append(f"movl ${target_label}, (%esp)")
    instr.append("ret")
    return instr, []


def transform_loop_instr(target_label):
    # loop-ul automat decrementeaza ecx, il compara cu 0 si daca e diferit de 0 sare la loop_start
    instr = []
    data_list = []
    sub_instr, sub_data = transform_sub("%ecx", "$1")  # rezultatul este pus in rez
    instr.extend(sub_instr)
    data_list.extend(sub_data)
    instr.append("mov rez, %ecx")  # luam rezultatul din rez si il punem in %ecx ca sa putem continua loop-ul normal

    cmp_instr, cmp_data = transform_cmp("%ecx", "$0")
    instr.extend(cmp_instr)
    data_list.extend(cmp_data)

    jump_instr, jump_data = transform_conditional_jump("jne", target_label)
    instr.extend(jump_instr)
    data_list.extend(jump_data)

    return instr, data_list


parse_and_transform(input_f, output_f)
input_f.close()
output_f.close()
