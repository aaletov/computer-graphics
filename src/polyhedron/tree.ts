export interface ITreeNode<Value> {
  value: Value;
  children: ITreeNode<Value>[];
}

export function createTreeNode<Value>(value: Value): ITreeNode<Value> {
  return {
    value: value,
    children: new Array<ITreeNode<Value>>(),
  };
}

export function coverList<Value>(tree: ITreeNode<Value>): Array<Value> {
  let nodes = new Array<Value>();
  function recursivePreorder(node: ITreeNode<Value>): void {
    nodes = nodes.concat(node.value);
    node.children.forEach((child: ITreeNode<Value>): void => {
      recursivePreorder(child);
      nodes = nodes.concat(node.value);
    });
  }
  recursivePreorder(tree);
  return nodes;
}
