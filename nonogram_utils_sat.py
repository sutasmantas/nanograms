#
# Make a transition (automaton) matrix from a
# single pattern, e.g. [3,2,1]
#
def make_transition_matrix(pattern):
    p_len = len(pattern)
    print("p_len:", p_len)
    num_states = p_len + sum(pattern)
    print("num_states:", num_states)
    t_matrix = []
    for i in range(num_states):
        row = []
        for j in range(2):
            row.append(0)
        t_matrix.append(row)

    # convert pattern to a 0/1 pattern for easy handling of
    # the states
    tmp = [0 for i in range(num_states)]
    c = 0
    tmp[c] = 0
    for i in range(p_len):
        for j in range(pattern[i]):
            c += 1
            tmp[c] = 1
        if c < num_states - 1:
            c += 1
            tmp[c] = 0
    print("tmp:", tmp)

    t_matrix[num_states - 1][0] = num_states
    t_matrix[num_states - 1][1] = 0

    for i in range(num_states):
        if tmp[i] == 0:
            t_matrix[i][0] = i + 1
            t_matrix[i][1] = i + 2
        else:
            if i < num_states - 1:
                if tmp[i + 1] == 1:
                    t_matrix[i][0] = 0
                    t_matrix[i][1] = i + 2
                else:
                    t_matrix[i][0] = i + 2
                    t_matrix[i][1] = 0

    print("The states:")
    for i in range(num_states):
        for j in range(2):
            print(t_matrix[i][j], end=" ")
        print()
    print()

    return t_matrix
