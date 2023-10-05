import { describe, expect, test, beforeEach } from '@jest/globals';
import { ITreeNode, coverList, createTreeNode } from './tree';

describe("Tree", () => {
  let tree: ITreeNode<number>;
  describe(("is root-only tree"), () =>{
    const expectedRoot = 1;
    beforeEach(() => {
      tree = createTreeNode(1);
    });
    test(("coverList contains one node"), () => {
      const list: Array<number> = coverList(tree);
      expect(list.length).toEqual(1);
      expect(list[0]).toEqual(expectedRoot);
    });
  });
  describe("is plain tree", () => {
    beforeEach(() => {
      tree = {
        value: 1,
        children: [
          {
            value: 2,
            children: [
              {
                value: 4,
                children: [],
              },
              {
                value: 5,
                children: [],
              },
            ],
          },
          {
            value: 3,
            children: [],
          },
        ],
      };
    })
    test("list is expected", () => {
      const expectedList: Array<number> = [1, 2, 4, 2, 5, 2, 1, 3, 1];
      expect(coverList(tree)).toEqual(expectedList);
    });
  });
});