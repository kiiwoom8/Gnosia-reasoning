import data
import handle_text as t
import table_rendering
from copy import deepcopy

undo_stack = []
redo_stack = []

def backup_state(stack = True):
    state = {
        'characters': deepcopy(data.characters),
        'removed_characters': deepcopy(data.removed_characters),
        'votes': deepcopy(data.votes),
        'voting_characters': deepcopy(data.voting_characters),
        'current_roles': deepcopy(data.current_roles),
        'matrix': deepcopy(data.matrix),
        'words_to_color': deepcopy(data.words_to_color),
        'participation': deepcopy(data.participation),
        'history': deepcopy(data.history),
        'ties': deepcopy(data.ties),
        'previous_ties': deepcopy(data.previous_ties),
        'first_attacker': data.first_attacker,
        'first_defender': data.first_defender,
        'target': data.target,
        'discussion_doubt': data.discussion_doubt,
        'discussion_defend': data.discussion_defend,
        'round': data.round,
    }
    if undo_stack and undo_stack[-1] == state:
        return

    if stack:
        undo_stack.append(state)
        redo_stack.clear()
    return state


def restore_state(state):
    data.characters = state['characters']
    data.removed_characters = state['removed_characters']
    data.votes = state['votes']
    data.voting_characters = state['voting_characters']
    data.current_roles = state['current_roles']
    data.matrix = state['matrix']
    data.words_to_color = state['words_to_color']
    data.participation = state['participation']
    data.history = state['history']
    data.ties = state['ties']
    data.previous_ties = state['previous_ties']
    data.first_attacker = state['first_attacker']
    data.first_defender = state['first_defender']
    data.target = state['target']
    data.discussion_doubt = state['discussion_doubt']
    data.discussion_defend = state['discussion_defend']
    data.round = state['round']


def undo():
    if undo_stack:
        state = undo_stack.pop()
        current = backup_state(False)
        redo_stack.append(current)
        restore_state(state)
        table_rendering.print_table()
    else:
        t.error_text = "\033[31mNo more actions to undo.\033[0m"


def redo():
    if redo_stack:
        state = redo_stack.pop()
        current = backup_state(False)
        undo_stack.append(current)
        restore_state(state)
        table_rendering.print_table()
    else:
        t.error_text = "\033[31mNo more actions to redo.\033[0m"