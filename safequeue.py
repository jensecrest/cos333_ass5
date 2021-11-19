#!/usr/bin/env python

#-----------------------------------------------------------------------
# safequeue.py
# Author: Bob Dondero
#-----------------------------------------------------------------------

from threading import RLock

# Each linked list node is implemented as a list with two elements.
# Element 0 references an item, and element 1 references the next
# node of the linked list.
_ITEM = 0
_NEXT = 1

class SafeQueue:

    def __init__(self):
        self._head_node = None
        self._tail_node = None
        self._lock = RLock()

    def put(self, item):
        with self._lock:
            new_node = [item, None]
            if self._tail_node is None:
                self._head_node = new_node
            else:
                self._tail_node[_NEXT] = new_node
            self._tail_node = new_node

    def get(self):
        with self._lock:
            if self._head_node is None:
                return None
            item = self._head_node[_ITEM]
            self._head_node = self._head_node[_NEXT]
            if self._head_node is None:
                self._tail_node = None
            return item
