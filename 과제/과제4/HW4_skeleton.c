#define _CRT_SECURE_NO_WARNINGS

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_TIME 99
#define MAX_TIMER_ID 31
#define TIMER_LABEL_WIDTH 6
#define TREE_PRINT_COLUMNS (MAX_TIMER_ID * 8)
#define TREE_PRINT_ROWS (MAX_TIMER_ID * 2 - 1)

typedef struct
{
    int expires;
    int id;
} Timer;

typedef struct TimerNode
{
    Timer timer;
    struct TimerNode *left;
    struct TimerNode *right;
} TimerNode;

/* 제공 함수 */
int compare_timer(Timer a, Timer b);
TimerNode *create_timer_node(Timer timer);
void print_timer(Timer timer);
void print_expired(Timer timer);
void destroy_tree(TimerNode *root);
int advance_time(TimerNode **root, int target);
int read_timers(TimerNode **root);

/* 분석 대상 X */
int measure_timer_tree(const TimerNode *root, int widths[], int centers[]);
void draw_timer_tree(const TimerNode *root, int origin, int row,
                     const int widths[], const int centers[],
                     char canvas[][TREE_PRINT_COLUMNS + 1], int *last_row);
void print_timer_tree(const TimerNode *root);

/* 구현할 함수 */
TimerNode *insert_timer(TimerNode *root, Timer timer);
const TimerNode *find_min_timer(const TimerNode *root);
TimerNode *delete_timer(TimerNode *root, Timer key, int *removed);
int print_timers(const TimerNode *root, int from, int to);

int compare_timer(Timer a, Timer b)
{
    if (a.expires < b.expires)
        return -1;
    if (a.expires > b.expires)
        return 1;
    if (a.id < b.id)
        return -1;
    if (a.id > b.id)
        return 1;
    return 0;
}

TimerNode *create_timer_node(Timer timer)
{
    TimerNode *node = (TimerNode *)malloc(sizeof(TimerNode));
    node->timer = timer;
    node->left = NULL;
    node->right = NULL;
    return node;
}

/* 출력 형식 고정을 위해 제공되는 함수 */
void print_timer(Timer timer)
{
    printf("TIMER %d %d\n", timer.expires, timer.id);
}

void print_expired(Timer timer)
{
    printf("EXPIRED %d %d\n", timer.expires, timer.id);
}

/* 분석 대상 X */
int measure_timer_tree(const TimerNode *root, int widths[], int centers[])
{
    int left_width, right_width, center, width;
    if (root == NULL)
        return 0;
    left_width = measure_timer_tree(root->left, widths, centers);
    right_width = measure_timer_tree(root->right, widths, centers);
    if (root->left != NULL && root->right != NULL)
    {
        width = left_width + 2 + right_width;
        center = (centers[root->left->timer.id] +
                  left_width + 2 + centers[root->right->timer.id]) /
                 2;
    }
    else if (root->left != NULL)
    {
        center = centers[root->left->timer.id] + 8;
        width = center + TIMER_LABEL_WIDTH / 2;
        if (width < left_width)
            width = left_width;
    }
    else if (root->right != NULL)
    {
        width = 8 + right_width;
        center = TIMER_LABEL_WIDTH / 2;
    }
    else
    {
        width = TIMER_LABEL_WIDTH;
        center = TIMER_LABEL_WIDTH / 2;
    }
    widths[root->timer.id] = width;
    centers[root->timer.id] = center;
    return width;
}

/* 분석 대상 X */
void draw_timer_tree(const TimerNode *root, int origin, int row,
                     const int widths[], const int centers[],
                     char canvas[][TREE_PRINT_COLUMNS + 1], int *last_row)
{
    int label_start, child_center, right_origin, column;
    char label[TIMER_LABEL_WIDTH + 1];
    if (root == NULL)
        return;
    label_start = origin + centers[root->timer.id] - TIMER_LABEL_WIDTH / 2;
    snprintf(label, sizeof(label), "%02d(%02d)", root->timer.expires, root->timer.id);
    memcpy(&canvas[row][label_start], label, TIMER_LABEL_WIDTH);
    if (row > *last_row)
        *last_row = row;
    if (root->left != NULL)
    {
        child_center = origin + centers[root->left->timer.id];
        for (column = child_center + 1; column < label_start; ++column)
            canvas[row][column] = '_';
        canvas[row + 1][child_center] = '/';
        draw_timer_tree(root->left, origin, row + 2, widths, centers, canvas, last_row);
    }
    if (root->right != NULL)
    {
        right_origin = origin + (root->left != NULL ? widths[root->left->timer.id] + 2 : 8);
        child_center = right_origin + centers[root->right->timer.id];
        for (column = label_start + TIMER_LABEL_WIDTH; column < child_center; ++column)
            canvas[row][column] = '_';
        canvas[row + 1][child_center] = '\\';
        draw_timer_tree(root->right, right_origin, row + 2,
                        widths, centers, canvas, last_row);
    }
}

/* 분석 대상 X */
void print_timer_tree(const TimerNode *root)
{
    int widths[MAX_TIMER_ID + 1] = {0};
    int centers[MAX_TIMER_ID + 1] = {0};
    int width, row, end, last_row = 0;
    char (*canvas)[TREE_PRINT_COLUMNS + 1];
    if (root == NULL)
    {
        printf("EMPTY\n");
        return;
    }
    width = measure_timer_tree(root, widths, centers);
    canvas = malloc(TREE_PRINT_ROWS * sizeof(*canvas));
    for (row = 0; row < TREE_PRINT_ROWS; ++row)
    {
        memset(canvas[row], ' ', (size_t)width);
        canvas[row][width] = '\0';
    }
    draw_timer_tree(root, 0, 0, widths, centers, canvas, &last_row);
    for (row = 0; row <= last_row; ++row)
    {
        end = width;
        while (end > 0 && canvas[row][end - 1] == ' ')
            end--;
        canvas[row][end] = '\0';
        printf("%s\n", canvas[row]);
    }
    free(canvas);
}

void destroy_tree(TimerNode *root)
{
    if (root == NULL)
        return;
    destroy_tree(root->left);
    destroy_tree(root->right);
    free(root);
}

int advance_time(TimerNode **root, int target)
{
    printf("TIME %d\n", target);
    while (*root != NULL)
    {
        const TimerNode *first = find_min_timer(*root);
        Timer expired;

        int removed;
        if (first == NULL)
        {
            printf("STATE_ERROR\n");
            return 0;
        }
        if (first->timer.expires > target)
            break;
        expired = first->timer;
        *root = delete_timer(*root, expired, &removed);
        if (!removed)
        {
            printf("STATE_ERROR\n");
            return 0;
        }
        print_expired(expired);
    }
    return 1;
}

int read_timers(TimerNode **root)
{
    int count, id;
    if (scanf("%d", &count) != 1 || count < 1 || count > MAX_TIMER_ID)
        return 0;
    for (id = 1; id <= count; id++)
    {
        Timer timer;
        if (scanf("%d", &timer.expires) != 1 ||
            timer.expires < 1 || timer.expires > MAX_TIME)
            return 0;
        timer.id = id;
        *root = insert_timer(*root, timer);
    }
    return 1;
}

TimerNode *insert_timer(TimerNode *root, Timer timer)
{
    return NULL;
}

const TimerNode *find_min_timer(const TimerNode *root)
{
    return NULL;
}

TimerNode *delete_timer(TimerNode *root, Timer key, int *removed)
{
    return NULL;
}

int print_timers(const TimerNode *root, int from, int to)
{
    return 0;
}

int main(void)
{
    TimerNode *root = NULL;
    int current_time = 0;
    int exit_code = 0;

    if (!read_timers(&root))
        exit_code = 1;

    while (exit_code == 0)
    {
        char command[16];
        int read_result = scanf("%15s", command);
        if (read_result != 1)
        {
            exit_code = 1;
            break;
        }
        if (strcmp(command, "EXIT") == 0)
            break;

        if (strcmp(command, "CANCEL") == 0)
        {
            Timer timer;
            int removed;
            if (scanf("%d %d", &timer.expires, &timer.id) != 2 ||
                timer.expires < 0 || timer.expires > MAX_TIME ||
                timer.id < 1 || timer.id > MAX_TIMER_ID)
            {
                exit_code = 1;
                break;
            }
            root = delete_timer(root, timer, &removed);
            printf("CANCEL %d %d %s\n", timer.expires, timer.id,
                   removed ? "OK" : "NOT_FOUND");
        }
        else if (strcmp(command, "NEXT") == 0)
        {
            const TimerNode *first = find_min_timer(root);
            if (first == NULL)
                printf("EMPTY\n");
            else
                printf("NEXT %d %d\n", first->timer.expires, first->timer.id);
        }
        else if (strcmp(command, "ADVANCE") == 0)
        {
            int target;
            if (scanf("%d", &target) != 1 ||
                target < current_time || target > MAX_TIME)
            {
                exit_code = 1;
                break;
            }
            current_time = target;
            if (!advance_time(&root, target))
            {
                exit_code = 2;
                break;
            }
        }
        else if (strcmp(command, "PRINT") == 0)
        {
            printf("PRINT\n");
            print_timer_tree(root);
        }
        else if (strcmp(command, "RANGE") == 0)
        {
            int from, to;
            if (scanf("%d %d", &from, &to) != 2 ||
                from < 0 || to > MAX_TIME || from > to)
            {
                exit_code = 1;
                break;
            }
            printf("RANGE %d %d\n", from, to);
            if (print_timers(root, from, to) == 0)
                printf("EMPTY\n");
        }
        else
        {
            exit_code = 1;
            break;
        }
    }

    if (exit_code == 1)
        printf("INPUT_ERROR\n");
    destroy_tree(root);
    return exit_code;
}
