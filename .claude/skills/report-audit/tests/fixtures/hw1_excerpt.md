# Banker 알고리즘 과제

처음에 Need 행렬을 손으로 그려 보면서 Max 와 Allocation 의 차를 정리했다. 그러다 공식 예시에서 요청량이 Available 을 넘을 때 어떻게 반려해야 하는지 헷갈려서 다시 교재를 뒤졌다. 시행착오 끝에 안전 상태 검사와 요청 처리를 두 단계로 나누어 작성했다. 처음 돌렸을 때는 T2 에서 종료가 너무 빨리 왔고, 디버거로 찾아보니 Need 를 갱신하는 부분을 빠뜨리고 있었다. 수정했더니 예시 출력과 맞았다.

**실제 출력**

```plain text
$ ./HW1
T  1: P1 R(1 2 0) → granted
T  2: P2 R(0 1 1) → granted
T  3: P1 R(0 0 1) → granted
```

![공식 예시 전체 실행 결과](https://example.com/hw1-case-run.png)

![은행원 반려 처리 결과](https://example.com/hw1-case-deny.png)

![안전 상태 검사가 중간에 실패한 사례](https://example.com/hw1-case-safe.png)

![시각화된 Need 행렬 변화](https://example.com/hw1-need.png)

**대화형 입력 예시**

```plain text
$ ./HW1
자원 종류 수를 입력하세요: 3
프로세스 수를 입력하세요: 4
```
