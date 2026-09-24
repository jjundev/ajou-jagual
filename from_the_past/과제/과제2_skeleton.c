#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <Windows.h>


typedef struct USER_info {
	char user;
	int direction;
	// 현재 위치, 이동할 위치에 대한 정보 포함 필요

}USER;

void init_map();
void print_map();
void set_map();
void start_point();
void update_map();
void moving();

int main() {

	char** map = NULL;
	int time = 0;

	USER usr = { }; // 구조체 초기화

	map = //맵 사용을 위한 2차원 배열 선언 
	
	init_map(map);

	start_point(map, &usr);
	set_map(map);

	printf("시간 : %d", time);
	time += 1;
	print_map(map);
	Sleep(1000);

	while (/*조건문 생성 필요*/) {
		printf("시간 : %d", time);
		update_map(map, &usr);
		Sleep(1000);
		time += 1;
	}
}
void init_map(char** map) {  // 맵 사용을 위한 메모리 설정 함수
	
}

void print_map(char** map) { // 현재 맵 상황을 출력해주는 함수, 동적메모리 할당으로 구현할것
	
}
void set_map(char** map) { // 맵에 탈출구를 위치시키는 함수
	//코드 작성
}
void start_point(char** map, USER* usr) { // 방탈출 술래의 시작점을 정하는 함수
	//코드 작성
}
void update_map(char** map, USER* usr) { // 맵의 실시간 상황 업데이트 하는 함수. 맵(배열)의 원소 값을 바꾸어준다.
	//코드 작성
}
void moving(char** map, USER* usr) { // 방탈출 술래의 이동과 정지를 담당하는 함수
	//코드 작성
}
