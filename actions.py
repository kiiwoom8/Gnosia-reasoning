import data
import table_rendering
import handle_text

t = handle_text.HandleText()
        
def act():
    while True:
        action_choice = select_action()
        if action_choice == data.Z:
            return
        if action_choice not in data.action_names:
            continue
        action_name = data.action_names[action_choice]
        if action_choice == data.VOTE:
            handle_vote(action_name)
        else:
            record_action(action_choice, action_name)

def record_action(action_choice: int, action_name: str, actor_target: list = None):
    actor_target = actor_target or []
    
    if actor_target:
        actor, target = actor_target[0], actor_target[1]
    else:
        # Get actor and validate
        actor, valid = get_actor(action_name)
        if not valid or actor in [data.Z, data.PASS]:
            return

        # Get target and validate
        target, valid = get_target(actor)
        if not valid or target in [data.Z, data.PASS]:
            return
    
    # Check if action is valid
    action = data.action_names_abbr.get(action_choice)
    if not action:
        t.print("\033[91mError: Invalid action choice.\033[0m")
        return

    # Record action in the matrix
    data.matrix[actor - 1][target - 1].append(action)
    target_name = data.characters.get(target, "Unknown Target")
    t.printr(f"\033[92mRecorded:\033[0m {data.characters[actor]} {action_name} {target_name}")

def handle_vote(action_name: str):
    action_choice = data.VOTE
    t.print("1. \033[91mStart the vote!\033[0m")
    t.print("2. Vote")
    t.print("z. Go back")
    
    vote_menu_choice = t.input("Select an action by number: ").strip().lower()

    if vote_menu_choice == '1':
        for num, char in data.characters.items():
            if char != " " and not char.startswith("Me") and char not in data.words_to_color:
                target, record = get_target(num)
                if target == data.Z:
                    return False  # Exit if 'Z' is selected
                elif target == data.PASS:
                    continue
                if record:
                    record_action(action_choice, action_name, [num, target])
    elif vote_menu_choice == '2':
        record_action(action_choice, action_name)

def get_actor(action_name):
    actor = select_character("acting", action_name)
    if actor in [data.Z, data.PASS]:
        return actor, False
    return actor, True

def get_target(actor, valid=True):
    if not valid:
        return data.INVALID, False

    # Loop to select target
    while True:
        target = select_character("target", f"Acting character: \033[91m{data.characters[actor]}\033[0m")
        if target in [data.Z, data.PASS]:
            return target, False
        elif actor == target:
            t.print("\033[31mCannot act on self. Please try again.\033[0m")
        else:
            return target, True
    
def display_characters():
    for number, character in data.characters.items():
        if character != " ":
            t.print(f"{number}. {character}")

def validate_choice(user_input):
    try:
        choice = int(user_input)
        if choice in data.characters.keys():
            if " " not in data.characters[choice]:
                return choice
            elif " " in data.characters[choice]:
                t.print("\033[31mRemoved character cannot be selected.\033[0m")
        else:
            t.print(f"\033[31mPlease enter a number between 1 and {max(data.characters.keys())}: \033[0m ")
    except ValueError:
        pass
    return data.INVALID

def delete_recent_action():
    while True:
        table_rendering.print_table()
        actor = select_character("actor")
        if actor is data.Z:
            return

        actor_name = data.characters[actor]
        target = select_character("target", f"Acting character: {actor_name}")
        if target is data.Z:
            return

        target_name = data.characters[target]
        actions = data.matrix[actor - 1][target - 1]

        if actions:
            removed_action = actions.pop()
            key = next((k for k, v in data.action_names_abbr.items() if v == removed_action), None)
            if key:
                removed_action = data.action_names.get(key)
            t.printr(f"\033[91mDeleted:\033[0m {actor_name} {removed_action} {target_name}")

def select_action():
    while True:
        t.print("Select the action performed:")
        for number, action_name in data.action_names.items():
            t.print(f"{number}. {action_name}")
        t.print("z. Go back")

        action_choice = t.input("Select an action by number: ").strip()

        if action_choice.lower() == 'z':
            return data.Z
        try:
            return int(action_choice)
        except ValueError:
            pass

def select_character(role_type, action_name=None):
    while True:
        if action_name:
            t.print(action_name)
        t.print(f"Select the {role_type} character:")
        user_input = t.input("Enter the number for your choice (OR 'p' to pass OR 'z' to go back): ").strip().lower()
        if user_input == 'z':
            return data.Z
        elif user_input == 'p':
            return data.PASS
        if (choice := validate_choice(user_input)) != data.INVALID:
            return choice

def assign_roles():
    while True:
        t.print("\033[92mAssign\033[0m/\033[91mremove\033[0m Roles: ")
        display_roles()
        role_choice = t.input("Select a role by number: ").strip()

        if role_choice.lower() == 'z':
            return

        role_choice = validate_role_choice(role_choice)
        if role_choice is data.INVALID:
            continue
        
        char_index = select_character("assigned/removed", f"\033[92mAssign\033[0m/\033[91mremove\033[0m a role ({data.role_symbols[role_choice]}): ")
        if char_index is data.Z:
            continue  

        handle_role_assignment(role_choice, char_index)

def display_roles():
    for key in data.role_names:
        t.print(f"{key}. {data.role_names[key]} ({data.role_symbols[key]})")
    t.print("z. Go back")

def validate_role_choice(role_choice):
    try:
        role_choice = int(role_choice)
        if role_choice not in data.role_symbols:
            t.print("\033[31mInvalid role choice. Try again.\033[0m")
            return data.INVALID
        return role_choice
    except ValueError:
        t.print("\033[31mInvalid input. Try again.\033[0m")
        return data.INVALID

def handle_role_assignment(role_choice, char_index):
    if role_choice in [9, 10]:
        toggle_color(char_index, role_choice)
    else:
        symbol = data.role_symbols[role_choice]
        toggle_role(char_index, symbol, data.role_names[role_choice])

def toggle_role(char_index, symbol, role_name):
    if symbol in data.characters[char_index]:
        data.characters[char_index] = data.characters[char_index].replace(symbol, "")
        t.printr(f"\033[91mRemoved\033[0m {role_name} ({symbol}) from {data.characters[char_index]}.")
    else:
        data.characters[char_index] += symbol
        t.printr(f"\033[94mAssigned\033[0m {role_name} ({symbol}) to {data.get_character_list()[char_index]}.")

def toggle_color(char_index, role_choice):
    character = data.get_character_list()[char_index]

    if role_choice == 9:
        color_code = "\033[31m"
        state = "\033[31mkilled\033[0m"
    else:
        color_code = "\033[34m"
        state = "\033[34mcold sleeped\033[0m"

    if character in data.words_to_color:
        removed_color = data.words_to_color.pop(character)
        if color_code == removed_color:
            t.printr(f"{character} is released from the state of being excepted.")
            return

    data.words_to_color[character] = color_code
    t.printr(f"{character} is {state}.")

def remove_character_from_list():
    while True:
        table_rendering.print_table()
        option = "\033[31mRemove character\033[0m"
        choice = select_character("target", option)
        if choice == data.Z:
            return
        elif len(data.characters.keys()) - list(data.characters.values()).count(" ") <= 2:
            t.printr("\033[31mThere should be at least 2 characters in the list.\033[0m")
        elif data.characters[choice][:2] == "Me":
            t.printr("\033[31mCannot remove the character of player.\033[0m")
        else:
            data.removed_characters[choice] = data.characters[choice]
            data.characters[choice] = " "
            t.printr(f"\033[31mRemoved\033[0m {data.removed_characters[choice]} from the list.")

def restore_removed_characters():
    for number, character in data.removed_characters.items():
        data.characters[number] = character
        t.printr(f"\033[94mRestored\033[0m {character} to the list.")
    data.removed_characters = {}

def exit_program():
    print("Exiting...")
    exit(0)