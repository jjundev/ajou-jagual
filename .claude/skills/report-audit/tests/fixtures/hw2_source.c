MemoryBlock *find_first_fit(MemoryList *list, int size) {
  MemoryBlock *current;

  if (list == NULL || size <= 0) {
    return NULL;
  }

  current = list->head.next;
  while (current != &list->head) {
    if (current->pid == FREE_PID && current->size >= size) {
      return current;
    }
    current = current->next;
  }
  return NULL;
}

int allocate_memory(MemoryList *list, int pid, int size) {
  if (list == NULL || pid <= 0 || size <= 0) {
    return 0;
  }
  if (find_process_block(list, pid) != NULL) {
    return 0;
  }

  MemoryBlock *block = find_first_fit(list, size);
  if (block == NULL) {
    return 0;
  }
  return 1;
}
