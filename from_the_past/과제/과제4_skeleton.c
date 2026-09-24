#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct Node {
    char question[100];
    char type_char_yes;  // MBTI 문자: Yes 선택 시
    char type_char_no;   // MBTI 문자: No 선택 시
    char mbti[5];        // 리프일 경우 완성된 MBTI
    struct Node* yes;
    struct Node* no;
} Node;

// MBTI 저장 포인터, mbti 노드 거리 계산용)
Node* mbti_nodes[16];
const char* mbti_labels[16] = {
    "ESTJ","ESTP","ESFJ","ESFP","ENTJ","ENTP","ENFJ","ENFP",
    "ISTJ","ISTP","ISFJ","ISFP","INTJ","INTP","INFJ","INFP"
};

//트리 구성을 위한 노드 설정
Node* create_node( ) {
    //
    // 빈칸에 코드 작성 필요
    //
    return node;
}

//마지막 노드인 리프를 구성
Node* create_leaf( ) {
    //
    // 빈칸에 코드 작성 필요
    //
    return node;
}


// 사용자로부터 yes / no를 입력받는 함수
char get_yes_no( ) {
    //
    // 빈칸에 코드 작성 필요
    //
}

// mbit 분류기 동작 
void traverse( ) {
    //
    // 빈칸에 코드 작성 필요
    //
}

// 리프 노드간 거리 계산 함수, 리프와 리프간 연결된 노드를 찾음
int find_path( ) {
    //
    // 빈칸에 코드 작성 필요
    //
}
// 리프 노드간 경로에 대한 거리값 리턴 
int get_distance( ) {
    //
    // 빈칸에 코드 작성 필요
    //
}


Node* get_mbti_node( ) {
    //
    // 빈칸에 코드 작성 필요
    //
}

// 트리 구성 함수, 루트를 구성하고 부모노드, 자식노드, 리프노드를 구성
Node* build_tree( ) {
    //
    // 빈칸에 코드 작성 필요
    //
}
//메인함수, 수정 가능
int main() {

    Node* root = build_tree();

    printf("=== MBTI 프로그램 ===\n");
    printf("1. MBTI 검사하기\n");
    printf("2. 두 MBTI 거리 비교하기\n");

    //
    // 빈칸에 코드 작성 필요
    //
}
