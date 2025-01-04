import data
import functions
import actions
import handle_text as t
import backup

def assign_roles():
    while True:
        t.check_error()
        t.t_print("\033[92mAssign\033[0m/\033[91mremove\033[0m Roles: ")
        display_roles()

        role_choice = t.t_input("Select a role by number: ")
        if role_choice:
            if role_choice == 'z':
                return
            role_choice = int(role_choice)
            if 0 < role_choice < len(data.roles) + 1:
                role_name = list(data.roles.keys())[role_choice - 1]
                char_index = actions.select_character("assigned/removed", 
                                                      f"{data.LGREEN}Assign{data.RESET}/{data.BLUSH}remove{data.RESET} a role ({data.roles[role_name]}): ")
                if char_index not in ['z', 'p']:
                    backup.backup_state()
                    toggle_role(int(char_index), role_name)
            else:
                t.error_text = "\033[31mInvalid choice. Try again.\033[0m"


def display_roles():
    for i, (role_name, role_symbol) in enumerate(data.roles.items(), start=1):
        t.t_print(f"{i}. {role_name} ({role_symbol})")
    t.t_print(" z. Go back")


def toggle_role(char_index, role_name):
    role_symbol = data.roles[role_name]
    if role_name in ["Killed", "Cold Sleep"]:
        functions.toggle_color(char_index, role_name)
        return
    if char_index in data.current_roles[role_name]:
        data.current_roles[role_name].remove(char_index)
        t.r_print(f"\033[91mRemoved\033[0m {role_name} ({role_symbol}) from {data.characters[char_index]}.")
    else:
        data.current_roles[role_name].append(char_index)
        char_index = int(char_index)
        t.r_print(f"\033[94mAssigned\033[0m {role_name} ({role_symbol}) to {data.characters[char_index]}.")