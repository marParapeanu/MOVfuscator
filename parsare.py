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
        transformed = process_instruction(line)
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

    # elif instruction.startswith("xor"):
    #     operands = parse_operands(operands_str)
    #     if len(operands) == 2:
    #         return transform_xor(operands[0], operands[1])
    #     else:
    #         return [line]
    #
    # elif instruction.startswith("or"):
    #     operands = parse_operands(operands_str)
    #     if len(operands) == 2:
    #         return transform_or(operands[0], operands[1])
    #     else:
    #         return [line]
    #
    elif instruction.startswith("and"):
        operands = parse_operands(operands_str)
        if len(operands) == 2:
            return transform_and(operands[0], operands[1])
        else:
            return [line]

    elif instruction.startswith("not"):
        operands = parse_operands(operands_str)
        if len(operands) == 2:
            return transform_not(operands[0], operands[1])
        else:
            return [line]

    elif instruction.startswith("dec"):
        operand = parse_operands(operands_str)
        if isinstance(operand, str):
            return transform_sub(operand, "$1")
        else:
            return [line]
    #
    # elif instruction.startswith("inc"):
    #     operand = parse_operands(operands_str)
    #     if isinstance(operand, str):
    #         return transform_add(operand, "$1")
    #     else:
    #         return [line]
    #
    elif instruction.startswith("cmp"):
        operands = parse_operands(operands_str)
        if len(operands) == 2:
            return transform_cmp(operands[0], operands[1])
        else:
            return [line]

    # elif instruction in ["je", "jge", "jg", "jl", "jle", "jne"]:
    #     target= operands_str.strip()
    #     return transform_jump(instruction, target)
    #
    #
    # elif instruction=="jmp":
    #     target=operands_str.strip()
    #     return transform_jmp(target) #nu e dependent de un cmp
    #
    #
    # elif instruction.startswith("lea"):
    #     operands = parse_operands(operands_str) #lea    v, %edi -> movl $v, %edi
    #     if len(operands) == 2:
    #         return tranform_lea(operands[0], operands[1])
    #     else:
    #         return [line]+

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
    main_instructions.append(
        f"movl {first_operand}, first_temp_storage")  # punem operanzii in memorie pentru a ii putea extrage pe bytes
    main_instructions.append(f"movl {second_operand}, second_temp_storage")
    for index in range(4):
        main_instructions.append(
            f"mov first_temp_storage+{index}, %ah")  # daca punem in ah o sa fie 256*first_index_operand si accesarea tabelului va fi ok
        main_instructions.append(
            f"mov second_temp_storage+{index}, %al")  # aici va fi valoarea byteului din second operand
        # ah=rand, #al = coloana
        main_instructions.append(
            f"movzbl %ax, %esi")  # ax = ah+al => retinem in esi indexul corect; movzbl muta ax in esi si umple restul cu 0
        main_instructions.append(f"movb sum_table(%esi), %cl")  # retinem suma partiala tot intr-un registru de un byte
        main_instructions.append(f"movb carry_sum_table(%esi), %dl")  # retinem carry-ul
        main_instructions.append(f"movb %cl, %ah")  # mutam suma partiala in ah pentru a aduna carry-ul, daca exista
        main_instructions.append(
            f"movb old_carry, %al")  # daca old_carry=0 =>suma partiala va fi suma finala, altfel adaugam 1
        main_instructions.append(
            f"movzbl %ax, %esi")  # noul index, practic cauta pe coloanele 0 sau 1, in functie de old carry
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
    # print(*main_instructions, sep='\n')
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


def transform_mul(first_operand, second_operand):
    local_instructions = []
    total_data = []

    instructions, cmp_data = transform_cmp(first_operand, second_operand)
    local_instructions.extend(instructions)
    total_data.extend(cmp_data)

    local_instructions.extend(create_choosing_table(first_operand, second_operand))

    local_instructions.append("mov times_8(global_value, zero_value, 1), global_value_times_8")
    local_instructions.append("mov choosing_table(global_value_times_8, zero_value, 1), first_operand")
    local_instructions.append("mov $1, one_value")
    local_instructions.append("mov choosing_table(global_value_times_8, one_value, 4), second_operand")
    # pana aici in first_operand se afla valoarea mai mare si in second_operand valoarea mai mica

    number_of_repetitions = 2 ** 16

    local_instructions.append("mov $0, counter")
    local_instructions.append("mov $0, repetitive_sound")

    for index in range(number_of_repetitions):
        local_instructions.extend(split_in_bytes("counter"))
        local_instructions.extend(split_in_bytes("second_operand"))
        local_instructions.extend(multiplicate_by_256("counter"))

        local_instructions.append("mov comparison_table(counter_3_times_256, second_operand_3, 1), global_value")
        local_instructions.append("mov comparison_table(counter_2_times_256, second_operand_2, 1), local_value")
        local_instructions.append("mov times_3(global_value, zero_value, 1), global_value_times_3")
        local_instructions.append("mov byte_comparison_table(global_value_times_3, local_value, 1), global_value")
        local_instructions.append("mov comparison_table(counter_1_times_256, second_operand, 1), local_value")
        local_instructions.append("mov times_3(global_value, zero_value, 1), global_value_times_3")
        local_instructions.append("mov byte_comparison_table(global_values_time_3, local_value, 1), global_value")
        local_instructions.append("mov comparison_table(counter_0_times_256, second_operand_0, 1), local_value")
        local_instructions.append("mov times_3(global_value, zero_value, 1), global_value_times_3")
        local_instructions.append("mov byte_comparison_table(global_value_times_3, zero_value, 1), global_value")
        local_instructions.append("mov decide_table(zero_value, global_value, 4), first_operand")

        instrs_add, data_add = transform_add("repetitive_sum", "first_operand")
        local_instructions.extend(instrs_add)
        data.extend(data_add)

        instrs_count, data_count = transform_add("counter", "one_value")
        local_instructions.extend(instrs_count)
        data.extend(data_count)

    local_instructions.append(f"mov repetitive_sum, {first_operand}")
    return local_instructions


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
    local_instructions.append(f"mov {first_operand}, first_operand_and")
    local_instructions.append(f"mov {second_operand}, second_operand_and")
    for index in range(4):
        local_instructions.append(f"movb first_operand_and + {index}, %al")
        local_instructions.append(f"movb second_operand_and + {index}, %bl")
        local_instructions.append("movb %al, first_byte_operand")
        local_instructions.append("movb %bl,second_byte_operand")
        local_instructions.extend(multiplicate_by_256("first_byte_operand"))
        local_instructions.append(f"movb and_table(byte_operand_times_256, second_byte_operand, 1), first_byte_operand")
        local_instructions.append(f"movb first_byte_operand, first_operand_and + {index}")
    # acum in first_operand_and se afla valoarea and-ului -> trebuie verificat daca valoarea este 0
    # il putem compara cu 0, folosind functia de compare
    return local_instructions


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


def transform_dec(first_operand):
    local_instructions = []
    total_data = []
    local_instructions.append("mov $1, one_value")
    instructions, data = transform_sub(first_operand, "one_value")
    local_instructions.append(instructions)
    total_data.append(data)
    return local_instructions, total_data


def transform_sub(first_operand, second_operand):
    all_instructions = []
    total_data = []

    lines_not, data_not = transform_not(first_operand)
    all_instructions.extend(lines_not)
    total_data.extend(data_not)

    lines_a1, data_a1 = transform_add(first_operand, second_operand)
    all_instructions.extend(lines_a1)
    total_data.extend(data_a1)

    lines_a2, data_a2 = transform_add(second_operand, 1)
    all_instructions.extend(lines_a2)
    total_data.extend(data_a2)

    return all_instructions, total_data


parse_and_transform(input_f, output_f)
input_f.close()
output_f.close()