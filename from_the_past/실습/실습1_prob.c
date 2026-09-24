#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <windows.h>

#define SCREEN_WIDTH 80
#define SCREEN_HEIGHT 30
#define MAX_PLAYERS 8

int num_players = 0;
int players[MAX_PLAYERS] = { 0 };

void greeting(int current_player);
void set_player();
void set_table();

void greeting(int current_player) {

}

void set_player() {
    
}

void set_table() {
    double PI = 3.14159;
    int radius_x = 15;
    int radius_y = 8;
    double angle_step = (2 * PI) / num_players;

    char board[SCREEN_HEIGHT][SCREEN_WIDTH];

    // 보드 초기화
    for (int i = 0; i < SCREEN_HEIGHT; i++) {
        for (int j = 0; j < SCREEN_WIDTH; j++) {
            board[i][j] = ' ';
        }
    }

    // 플레이어 배치
    for (int i = 0; i < num_players; i++) {
        double angle = i * angle_step;
        int x = (int)(radius_x * cos(angle)) + SCREEN_WIDTH / 2;
        int y = (int)(radius_y * sin(angle)) + SCREEN_HEIGHT / 2;

        if (x >= 0 && x < SCREEN_WIDTH && y >= 0 && y < SCREEN_HEIGHT) {
            board[y][x] = '0' + (i + 1);
        }
    }

    // 테이블 출력
    for (int i = 0; i < SCREEN_HEIGHT; i++) {
        for (int j = 0; j < SCREEN_WIDTH; j++) {
            printf("%c", board[i][j]);
        }
        printf("\n");
    }
}

int main() {

    return 0;
}
