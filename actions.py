import data
import table_rendering
import handle_text as t
import vote
import backup
        
def handle_discussion():
    while True:
        var, action_range = print_discusstion_menu()        
        discussion_menu_choice = t.t_input("Select an action by number: ")
        if discussion_menu_choice:
            if discussion_menu_choice in ['z', 'p']:
                return
            if discussion_menu_choice == '0':
                backup.backup_state()
                init_discussion_settings()
                increment_round()
                table_rendering.print_table()
            elif discussion_menu_choice.isdigit() and int(discussion_menu_choice) + var in action_range:
                discussion_menu_choice = int(discussion_menu_choice) + var
                backup.backup_state()
                record_action(discussion_menu_choice, data.action_list[discussion_menu_choice]["Name"], data.actor, data.target)
                table_rendering.print_table()
            else:
                t.error_text = "\033[31mInvalid choice. Try again.\033[0m"


def print_discusstion_menu():
    t.check_error()
    var = 0
    if data.round > 5 and data.ties_round in [0, 3]: # Voting round
        vote.handle_vote()
        return 0, []
    elif data.discussion_doubt:
        var = 2
        action_range = range(3, 8)
    elif data.discussion_defend:
        t.t_print(f"Target: {data.BLUE}{data.characters[data.target]}{data.RESET}")
        var = 7
        action_range = range(8, 12)
    else: # Beginning; Doubt or Cover
        action_range = range(1, 3)

    for i in action_range:
        action = data.action_list[i]
        t.t_print(f"{i - var}. {action['Color']}{action['Name']}{data.RESET}")
    t.t_print("0. End discussion")
    if data.vote_history:
        t.t_print(f"r. {data.RED}Revert the most recent votes{data.RESET}")
    t.t_print("z. Go back")
    return var, action_range


def init_discussion_settings():
    data.first_actor, data.actor, data.target = None, None, None
    data.discussion_doubt, data.discussion_defend = False, False


def increment_round():
    if data.ties:
        data.ties_round += 1
    else:
        data.round += 1    


def record_action(action_choice: int, action_name: str, actor = None, target = None):
    if action_name == f"{data.RED}Retaliate/Don't be fooled{data.RESET}":
        actor = data.target
        data.target = data.first_actor
        target = data.target
    if not actor:
        if target:
            t.t_print(f"Target: {data.BLUE}{data.characters[target]}{data.RESET}" )
        actor = select_character("acting", action_name)
        if  actor in ['z', 'p']:
            return
        actor = int(actor)
        if actor == target:
            t.error_text = "\033[31mCannot act on self. Please try again.\033[0m"
            return
        data.actor = actor
    if not target:
        target = get_target(actor)
        if target in ['z', 'p']:
            return
        target = int(target)
        data.target = target
        
    action = data.action_list.get(action_choice, {}).get("Abbr")
    data.matrix[actor - 1][target - 1].append(action)
    target_name = data.characters.get(target, "\033[31mUnknown\033[0m")
    t.r_print(f"\033[92mRecorded:\033[0m {data.characters[actor]} {action_name} {target_name}")
    set_discussion_options(action_choice)


def set_discussion_options(action_choice):
    match action_choice:
        case 1:
            data.discussion_doubt = True
            data.first_actor = data.actor
        case 2:
            data.discussion_defend = True
        case 6:
            data.discussion_doubt = True
            data.discussion_defend = False
        case 7:
            data.discussion_doubt = False
            data.discussion_defend = True
        case 11:
            data.discussion_doubt = True
            data.discussion_defend = False
    data.actor = None


def get_target(actor):
    while True:
        target = select_character("target", f"Acting character: {data.BLUSH}{data.characters[actor]}{data.RESET}")
        if target in ['z', 'p']:
            return target
        if actor == int(target):
            t.t_print("\033[31mCannot act on self. Please try again.\033[0m")
        elif data.ties and int(target) not in data.ties:
            t.t_print("\033[31mInvalid choice. Please try again.\033[0m")
        else:
            return target


def display_characters():
    for number, character in data.characters.items():
        if character != " ":
            t.t_print(f"{number}. {character}")


def validate_choice(user_input:str, choice_type='character'):
    if user_input.isdigit():
        choice = int(user_input)
        valid_data = data.characters if choice_type == 'character' else data.roles
        if choice in valid_data and (choice_type != 'character' or " " not in valid_data[choice]) or not user_input:
            return choice
        else:
            return False
    else:
        return False


def delete_recent_action(actor = None, target = None):
    while True:
        if not actor or not target:
            actor = select_character("actor")
            if actor in ['z', 'p']:
                return
            actor = int(actor)
            target = select_character("target", f"Acting character: \033[91m{data.characters[actor]}\033[0m")
            if target == 'z':
                return
            target = int(target)
            remove_action_from_table(actor, target)
            actor = None
        else:
            remove_action_from_table(actor, target)
            return


def remove_action_from_table(actor, target):
    backup.backup_state()
    actor_name = data.characters[actor]
    target_name = data.characters[target]
    actions = data.matrix[actor - 1][target - 1]
    if actions:
        removed_action = actions.pop()
        key = next((action_num for action_num, action in data.action_list.items() if action["Abbr"] == removed_action), None)
        if key:
            removed_action = data.action_list[key]
        t.r_print(f"\033[91mDeleted:\033[0m {actor_name} {removed_action['Name']} {target_name}")
        table_rendering.print_table()
    else:
        t.error_text = "\033[31mNo actions to delete.\033[0m"


def select_character(role_type, action_name=None):
    while True:
        t.check_error()
        if action_name:
            t.t_print(action_name)
        if data.ties:
            most_voted_names = [data.characters[char_index] for char_index in data.ties]
            t.t_print(f"Select the {role_type} character from the following: {most_voted_names}")            
        else:
            t.t_print(f"Select the {role_type} character:")
        user_input = t.t_input("Enter the number for your choice (OR 'p' to pass OR 'z' to go back): ")
        if user_input:
            if user_input in ['z', 'p'] or validate_choice(user_input):
                return user_input
            else:
                t.error_text = "\033[31mInvalid choice. Try again.\033[0m"


def assign_roles():
    while True:
        t.check_error()
        t.t_print("\033[92mAssign\033[0m/\033[91mremove\033[0m Roles: ")
        display_roles()
        role_choice = t.t_input("Select a role by number: ")
        if role_choice:
            if role_choice == 'z':
                return
            if validate_choice(role_choice, 'role'):
                role_choice = int(role_choice)
                char_index = select_character("assigned/removed", f"\033[92mAssign\033[0m/\033[91mremove\033[0m a role ({data.roles[role_choice]["Symbol"]}): ")
                if char_index not in ['z', 'p']:
                    backup.backup_state()
                    toggle_role(int(char_index), role_choice)
            else:
                t.error_text = "\033[31mInvalid choice. Try again.\033[0m"


def display_roles():
    for role_num, role in data.roles.items():
        formatted_num = f" {role_num}" if role_num < 10 else str(role_num)
        t.t_print(f"{formatted_num}. {role["Name"]} ({role["Symbol"]})")
    t.t_print(" z. Go back")


def toggle_role(char_index, role_choice):
    role_name = data.roles[role_choice]["Name"]
    role_symbol = data.roles[role_choice]["Symbol"]
    if role_name in ["Killed", "Cold Sleep"]:
        toggle_color(char_index, role_choice)
        return
    if char_index in data.current_roles[role_name]:
        data.current_roles[role_name].remove(char_index)
        t.r_print(f"\033[91mRemoved\033[0m {role_name} ({role_symbol}) from {data.characters[char_index]}.")
    else:
        data.current_roles[role_name].append(char_index)
        char_index = int(char_index)
        t.r_print(f"\033[94mAssigned\033[0m {role_name} ({role_symbol}) to {data.characters[char_index]}.")


def toggle_color(char_index, role_choice):
    if role_choice == 9:
        color_code = "\033[31m"
        state = "\033[31mkilled\033[0m"
    elif role_choice == 10:
        color_code = "\033[34m"
        state = "\033[34mcold sleeped\033[0m"

    if data.characters[char_index] in data.words_to_color and data.words_to_color[data.characters[char_index]] == color_code:
        removed_color = data.words_to_color.pop(data.characters[char_index])
        if color_code == removed_color:
            t.r_print(f"{data.characters[char_index]} is released from the state of being excepted.")
            return

    data.words_to_color[data.characters[char_index]] = color_code
    t.r_print(f"{data.characters[char_index]} is {state}.")


def remove_character_from_list():
    while True:
        table_rendering.print_table()
        t.check_error()
        option = "\033[91mRemove character\033[0m"
        choice = select_character("target", option)
        if choice == 'z':
            return
        choice = int(choice)
        if len(data.characters.keys()) - list(data.characters.values()).count(" ") <= 2:
            t.error_text = "\033[31m[Failed] There should be at least 2 characters in the list.\033[0m"
        elif data.characters[choice][:2] == "Me":
            t.error_text = "\033[31mCannot remove the character of player.\033[0m"
        else:
            backup.backup_state()
            data.removed_characters[choice] = data.characters[choice]
            data.characters[choice] = " "
            t.r_print(f"\033[31mRemoved\033[0m {data.removed_characters[choice]} from the list.")


def restore_removed_characters():
    if not data.removed_characters:
        t.error_text = "\033[31mNo characters to restore.\033[0m"
        return
    for number, character in data.removed_characters.items():
        data.characters[number] = character
    t.r_print(f"\033[94mRestored all the characters to the list.\033[0m")
    data.removed_characters = {}