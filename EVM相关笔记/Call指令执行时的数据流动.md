# 学习记录

## 问题1--call执行时的数据流动以及各存储区的角色

### 角色分配

1. storage：存储账户地址->账户信息的映射。
2. memory：交易执行过程中的临时存储空间，保存一些执行过程中涉及到引用变量（struct，String，Bytes，动态数组等）、返回值等。
3. stack：EVM是基于堆栈的虚拟机，操作是通过操作数出栈，执行操作，结果入栈来完成的；因此EVM执行过程中涉及到计算的数据都会入栈以进行计算。
4. calldata：一块只读的数据区，保存了合约调用过程的calldata

在一次call中：

```
storage -> 存储call执行过程中读写的状态变量
memory  -> call执行过程中用到的引用类型变量、参数、执行返回值
stack   -> call执行过程中用到的简单类型变量
calldata-> call执行过程中用到的calldata
```



### 数据流动

![image-20240106220713377](C:\Users\kaka\Desktop\EVM相关笔记\img\执行call指令时的数据流动.png)

## 自实现堆栈，实现一些指令

## 问题2

### 当在字节码内遇到CALL时，stack和memory怎么进行状态切换

1. call指令的执行需要参数，一些参数会在stack中，calldata是保存在一块专门存放calldata的特殊区域的，它也是memory的一部分。

```
最初的stack状态切换：
stack弹出一系列call指令的参数
calldata从calldata数据区读取到stack中，而后也弹出
```

2. 执行指令的参数以及出栈，接下来读取到call指令，则执行该指令

   ```
   执行call指令时，因为会进入到新的合约上下文，所以
   执行时的状态切换
   stack会切换为新上下文中新创建的栈实例
   memory会切换为新上下文中新创建的内存实例
   在新的上下文中执行该指令
   ```



### CALL，CALLCODE，STATICCALL，DELEGATECALL之间在字节码层面的区别

1. CALL指令：F1

   ```
   call指令会在执行时创建新的上下文，会在新的上下文中执行接下来的操作。
   ```

2. CALLCODE指令：F2

   ```
   callcode指令与delegatecall指令的执行逻辑相同，会在当前上下文执行被调用合约中的逻辑，
   但是其callcode过程中的msg.sender会随着上下文的变化而变化
   ```

   ![image-20240106225409469](C:\Users\kaka\AppData\Roaming\Typora\typora-user-images\image-20240106225409469.png)

3. DELEGATECALL：F4

   ```
   delegatecall指令会在当前上下文执行被调用合约中的逻辑，并且，其delegatecall过程中的msg.sender
   一直都是最初的caller
   ```

   ![image-20240106225318640](C:\Users\kaka\AppData\Roaming\Typora\typora-user-images\image-20240106225318640.png)

4. STATICCALL指令：FA

```
staticCall指令会在执行时创建新的上下文，会在新的内存实例，新的栈实例中执行接下来的操作。但是，staticCall不允许在新的上下文中执行任何修改状态的指令，也就是只能调用pure，view修饰的函数
```

