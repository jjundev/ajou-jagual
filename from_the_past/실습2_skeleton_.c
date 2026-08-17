#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <Windows.h>

#define ROW 8
#define COL 8

typedef struct chess_piece {
	
}CP;

void init_board(char** board);
void set_board(char** board, CP king, CP queen);
void print_board(char** board, CP king, CP queen);


int main() {


}
void init_board(char** board) { // 메모리 초기화, 0으로 채우기
	for (int i = 0; i < ROW; i++)
		memset(board[i], 0, COL);
}
void set_board(char** board, CP king, CP queen) { // 체스판 설정

}
void print_board(char** board, CP king, CP queen) { // 현재 체스판의 기물 위치를 출력
	
}
