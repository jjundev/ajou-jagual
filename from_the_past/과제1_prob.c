#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <windows.h>

#define SCREEN_WIDTH 80
#define SCREEN_HEIGHT 30
#define MAX_PLAYERS 8

int bullet_loc = 0;
int num_players = 0;
int players[MAX_PLAYERS] = { 0 };

void russian_roulette();
void set_bullet();
void set_player();
void set_table();
void remove_player();

void russian_roulette(int current_player) {

 //재귀호출로 게임 진행
}


void set_bullet() {
     // 0~7번째 탄창에 총알 랜덤 장전
}

void set_player() {
     //올바른 인원수를 입력할때까지 재귀함수를 통해 다시 구현
       
}

void set_table() {
    double PI = 3.14159; // 선언된 각 변수의 역할 (ex. 실행 창에서 숫자를 원형으로 배치하기 위한 원주율 값 정의)
    int radius_x = 15; // ....
    int radius_y = 8;// ....
    double angle_step = (2 * PI) / num_players;// ....

    char board[SCREEN_HEIGHT][SCREEN_WIDTH]; // ...

    //실행 창에서 표시되는 원형 테이블의 형태를 SCREEN_WIDTH 만큼 가로 축 길이, SCREEN_HEIGHT만큼 세로축의 길이만큼 표현하기 위해 반목문을 통한 
    for (int i = 0; i < SCREEN_HEIGHT; i++) {
        for (int j = 0; j < SCREEN_WIDTH; j++) {
            board[i][j] = ' ';
        }
    }

    int active_players = 0;
    for (int i = 0; i < MAX_PLAYERS; i++) {
        if (players[i] == 1) {
            active_players++;
        }
    }

    double active_angle_step = (2 * PI) / active_players;
    int placed = 0;

    for (int i = 0; i < MAX_PLAYERS; i++) {
        if (players[i] == 1) {
            double angle = placed * active_angle_step;
            int x = (int)(radius_x * cos(angle)) + SCREEN_WIDTH / 2;
            int y = (int)(radius_y * sin(angle)) + SCREEN_HEIGHT / 2;

            if (x >= 0 && x < SCREEN_WIDTH && y >= 0 && y < SCREEN_HEIGHT) {
                board[y][x] = '0' + (i + 1);
            }
            placed++;
        }
    }

    for (int i = 0; i < SCREEN_HEIGHT; i++) {
        for (int j = 0; j < SCREEN_WIDTH; j++) {
            printf("%c", board[i][j]);
        }
        printf("\n");
    }
}

void remove_player(int player) {
 
}

int main() {
    set_player();
    printf("지금부터 러시안 룰렛 게임을 시작합니다!\n");
    set_bullet();
    set_table();
    russian_roulette();
    return 0;
}
