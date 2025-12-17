# **计算机象棋算法深度剖析：Alpha-Beta 剪枝与价值表体系的理论与实践**

## **1\. 绪论：中国象棋的计算复杂性与引擎架构**

中国象棋（Xiangqi），作为一种古老而充满智慧的零和博弈游戏，其在人工智能领域的探索历史几乎与国际象棋（Chess）同步，但由于其独特的规则特性——如“九宫”限制、“隔山打牛”的炮、以及复杂的“长将/长捉”判例——使得其算法实现具有独特的挑战性。用户所关心的核心问题——“Alpha-Beta 剪枝”与“价值表（Piece-Square Tables）”如何应用于算法——实际上触及了现代博弈引擎的两个灵魂支柱：**搜索（Search）与评估（Evaluation）**。

本报告将从底层数学原理到高层工程实现，对中国象棋引擎的内部机理进行详尽的解构。我们将探讨计算机如何通过 Alpha-Beta 算法在庞大的博弈树中寻找最优解，以及如何利用价值表（PST）将复杂的局面直觉转化为机器可理解的数值。

### **1.1 状态空间复杂度与博弈树**

在讨论具体算法之前，必须理解中国象棋的计算规模。与国际象棋相比，中国象棋的棋盘更大（9x10 共 90 个交叉点，对比国际象棋的 8x8 共 64 个格），这导致了状态空间复杂度的指数级增长。

* **状态空间复杂度（State-Space Complexity）：** 据估算，中国象棋的合法局面数量约为 $10^{40}$ 至 $10^{48}$ 级别，略高于国际象棋 1。
* **博弈树复杂度（Game-Tree Complexity）：** 这一指标更为关键，它代表了从初始局面开始，所有可能对局路径的总和。中国象棋的平均分支因子（Branching Factor，即每一回合平均有多少种合法走法）在开局和中局阶段通常在 40 到 50 之间，而国际象棋约为 35。这意味着中国象棋的搜索树在相同深度下比国际象棋更宽，对剪枝算法的效率要求更高 3。

### **1.2 现代象棋引擎的架构分层**

一个标准的象棋引擎（如 ElephantEye, Wukong, Pikafish）通常由以下几个模块紧密耦合而成：

1. **局面表示（Board Representation）：** 负责维护棋盘状态，生成合法着法。常见的有 0x88 数组、位棋盘（Bitboards）等 5。
2. **搜索核心（Search Kernel）：** 负责“向前看”。即通过模拟未来的走法，构建博弈树。Alpha-Beta 剪枝正是这一层的核心算法，用于在有限时间内尽可能深地探索局面 7。
3. **静态评估（Static Evaluation）：** 负责“判断当下”。当搜索到达一定深度停止时，评估函数会对当前局面打分。价值表（PST）是这一层最基础也是最高效的数据结构 9。
4. **置换表（Transposition Table）：** 也就是哈希表，用于记忆已经搜索过的局面，避免重复计算 11。

接下来的章节将深入剖析 Alpha-Beta 与价值表在这套架构中是如何协同工作的。

---

**2\. 博弈树搜索核心：Alpha-Beta 剪枝机制**

Alpha-Beta 剪枝并非一种独立的启发式策略，而是对\*\*极小化极大算法（Minimax Algorithm）\*\*的一种数学上严格无损的优化。其核心思想在于：如果在搜索过程中发现某一分支的局面已经劣于之前搜索过的某个选择，那么就没有必要继续深入分析该分支的剩余部分，因为理性的对手绝不会允许该局面的发生 7。

### **2.1 极小化极大（Minimax）的数学基础**

在零和博弈中，一方的收益即为另一方的损失。

* **Max 层（红方）：** 总是选择评分最高的着法。
* **Min 层（黑方）：** 总是选择评分最低的着法（即对红方最不利，对黑方最有利）。

假设搜索深度为 $d$，分支因子为 $b$，传统的 Minimax 算法必须遍历所有 $b^d$ 个叶子节点才能得出结论。在中国象棋中，如果搜索深度达到 10 层（这在现代引擎中仅算浅层搜索），节点数将达到 $40^{10} \approx 10^{16}$，这在计算上是不可接受的。

### **2.2 Alpha-Beta 剪枝的运作机理**

Alpha-Beta 算法引入了两个参数 $\alpha$ 和 $\beta$，这两个参数构成了搜索窗口（Search Window），并在递归过程中不断传递和收缩。

#### **2.2.1 参数定义**

* **Alpha ($\alpha$)：** 当前搜索路径上，MAX 节点（红方）已经找到的最好着法的最低保底收益。任何低于 $\alpha$ 的局面红方都不会考虑，因为红方已经有更好的选择了。$\alpha$ 初始化为 $-\infty$。
* **Beta ($\beta$)：** 当前搜索路径上，MIN 节点（黑方）已经找到的对红方限制的最大上限。任何高于 $\beta$ 的局面黑方都不会允许发生，因为黑方已经有其它着法可以让红方收益更低。$\beta$ 初始化为 $+\infty$。

#### **2.2.2 剪枝逻辑（Cutoff）**

剪枝发生在 $\beta \leq \alpha$ 的时刻。

* **Beta 剪枝（Beta Cutoff）：** 当算法在 MAX 节点的一个子节点中发现一个分值 $v \geq \beta$ 时，意味着这个走法太好了（对红方太有利），位于上层的 MIN 节点（黑方）不会选择这条路径，因此 MAX 节点可以直接返回 $\beta$。
* **Alpha 更新：** 当 MAX 节点发现一个分值 $v > \alpha$ 时，更新 $\alpha = v$，表示红方找到了一个更好的保底手段。

#### **2.2.3 算法伪代码解析（基于 Negamax 框架）**

在实际工程实现中（如 Wukong 或 ElephantEye），通常使用 Negamax 框架来简化代码，利用 $\max(a, b) = -\min(-a, -b)$ 的性质，使得红黑双方的代码逻辑对称。

```C++

// Alpha-Beta 搜索伪代码 (Negamax 形式)
int AlphaBeta(Position& pos, int depth, int alpha, int beta) {
    // 1\. 叶子节点或游戏结束，调用评估函数（价值表在此处发挥作用）
    if (depth \== 0 |

| pos.isGameOver()) {
        return QuiescenceSearch(pos, alpha, beta); // 进入静态搜索
    }

    // 2\. 查置换表 (Transposition Table)
    int ttScore \= TT.probe(pos.zobristKey, depth, alpha, beta);
    if (ttScore\!= INVALID) return ttScore;

    int bestScore \= \-INFINITY;
    Move bestMove \= NO\_MOVE;

    // 3\. 生成着法并排序 (Move Ordering)
    MoveList moves \= pos.generateMoves();
    sortMoves(moves); // 关键步骤：好的排序能极大提高剪枝效率

    // 4\. 遍历所有着法
    for (Move m : moves) {
        pos.makeMove(m);
        // 递归调用，注意 alpha 和 beta 的翻转与取反
        int score \= \-AlphaBeta(pos, depth \- 1, \-beta, \-alpha);
        pos.unmakeMove(m);

        if (score \>= beta) {
            // Beta 剪枝：对手不会允许这种局面发生
            TT.store(pos.zobristKey, beta, LOWER\_BOUND, depth, m);
            return beta;
        }
        if (score \> bestScore) {
            bestScore \= score;
            bestMove \= m;
            if (score \> alpha) {
                alpha \= score; // 提升 Alpha 下界
            }
        }
    }

    // 5\. 存储结果到置换表
    int flag \= (bestScore \> alphaOriginal)? EXACT : UPPER\_BOUND;
    TT.store(pos.zobristKey, bestScore, flag, depth, bestMove);

    return bestScore;
}
```

### **2.3 着法排序（Move Ordering）：Alpha-Beta 的生命线**

用户必须理解，Alpha-Beta 剪枝的效率完全取决于**先搜索哪些着法**。

* **最差情况：** 如果引擎总是先搜索最差的着法，那么 $\\alpha$ 和 $\\beta$ 永远不会更新到足以触发剪枝的程度，算法退化为 $O(b^d)$ 的 Minimax 3。
* **最佳情况：** 如果引擎每次都能猜中“最佳着法”并第一个搜索，剪枝效率最大化，复杂度降为 $O(b^{d/2})$。这意味着在同样时间内，引擎可以搜索的深度是原来的两倍 14。

在中国象棋算法中，着法排序通常遵循以下优先级：

1. **置换表着法（Hash Move）：** 上一次搜索该局面时发现的最佳着法。这是最可靠的 11。
2. **吃子着法（MVV-LVA）：** “最有价值受害者-最无价值攻击者”启发式。例如，用卒吃车（LVA 1 吃 MVV 9）的优先级极高，而用车吃卒的优先级较低。价值判定直接依赖于**价值表**中的材质分 17。
3. **杀手着法（Killer Moves）：** 在搜索树的同一深度下，曾经在其他兄弟节点引发过剪枝的着法（通常是强力的战术手段，如弃子攻杀）5。
4. **历史启发（History Heuristic）：** 在整个搜索过程中，历史上表现好的着法（不论在哪个深度）给予加分 9。

---

**3\. 启发式评估系统：价值表与局面量化**

搜索算法解决了“如果走这一步会发生什么”的问题，而评估函数（Evaluation Function）则解决“这个局面到底好不好”的问题。当 Alpha-Beta 搜索到指定深度（例如第 10 层）停止时，它必须调用 Evaluate() 函数来获取一个数值。

用户询问的“价值表”在专业术语中称为 **Piece-Square Table (PST)**，即**子力-位置价值表**。它是传统象棋引擎（如 ElephantEye, Sachy, 早期 Wukong）评估函数的核心基石 9。

### **3.1 价值表的结构与原理**

价值表本质上是一个二维数组（或一维映射），为每一种棋子在棋盘上的每一个位置分配一个固定的分数。

$$ \text{TotalScore} = \sum_{p \in \text{Pieces}} (\text{MaterialValue}(p) + \text{PST}_p) $$
这个公式表明，一个棋子的价值由两部分组成：

1. **材质价值（Material Value）：** 棋子本身的固有价值。
2. **位置价值（Positional Value）：** 棋子在特定位置的加成或扣分。

#### **3.1.1 典型材质分设置**

$$\text{TotalScore} = \sum_{p \in \text{Pieces}} (\text{MaterialValue}(p) + \text{PST}_p)$$
根据中国象棋的战术特点，通用的材质分（以车为基准或以兵为基准）如下表所示 19：

| 棋子类型             | 传统分值                | 引擎内部估值 (Centipawns) | 战术特性                 |
| :------------------- | :---------------------- | :------------------------ | :----------------------- |
| **帅/将 (King)**     | $\infty$               | 20000+                    | 游戏结束条件             |
| **车 (Rook)**        | 9                       | 900–1000                  | 最强战力，控制纵横       |
| **炮 (Cannon)**      | 4.5                     | 450–500                   | 依赖炮架，开局强，残局弱 |
| **马 (Horse)**       | 4                       | 400–450                   | 八面威风，但受绊马腿限制 |
| **象/相 (Elephant)** | 2                       | 200–250                   | 纯防御，不过河           |
| **士/仕 (Advisor)**  | 2                       | 200                       | 护卫九宫                 |
| **兵/卒 (Pawn)**     | 1 (过河前) / 2 (过河后) | 100 / 200                 | 过河后价值倍增           |

### **3.2 价值表（PST）的具体设计逻辑**

价值表不仅仅是数字的堆砌，它编码了人类大师的象棋理论。以下通过具体棋子的 PST 示例来解析其背后的算法逻辑。

#### **3.2.1 兵/卒的价值表设计**

中国象棋中，卒子过河顶大车。卒的价值随位置变化极大。

* **未过河：** 只能向前，且容易被对方巡河炮或高车捉死，价值最低。
* **过河（第 3/4 线）：** 威胁增大，可以横走，价值提升。
* **逼近九宫（第 1/2 线）：** 威胁老将，价值达到巅峰。
* **沉底（底线）：** “老卒无功”，只能横走且容易被做掉，价值大幅回落 19。

PST 数组示例（红兵，简化版）：

```text
# 列号: 0 1 2 3 4 5 6 7 8
[0, 0, 0, 0, 0, 0, 0, 0, 0]            # 敌方底线：老卒，价值低 (e.g., +0)
[10, 20, 30, 40, 40, 30, 20, 10, 0]   # 敌方下二路：威胁极大 (e.g., +40)
[10, 20, 30, 40, 40, 30, 20, 10, 0]   # 敌方下三路：控制要津
[5, 10, 20, 30, 30, 20, 10, 5, 0]     # 敌方兵行线：刚过河
[0, 5, 0, 5, 0, 5, 0, 5, 0]          # 河界：准备过河
[0, 0, 0, 0, 0, 0, 0, 0, 0]          # 己方河界
```

(注：实际引擎中为了计算速度，通常使用一维数组存储 90 个值)

#### **3.2.2 马的价值表与“窝心马”惩罚**

马在棋盘中央（中宫）控制点最多（8个），但在边角控制点减少。

* **盘河马：** 位于河口，进可攻退可守，PST 给予高分。
* **窝心马（归心马）：** 马跳入己方九宫中心（坐标 1,4 或 8,4），极易阻挡老将移动导致“闷宫”杀棋。因此，PST 在这个特定的坐标点会给予显著的**负分**（Penalty），告诉引擎“除非万不得已，不要跳到这里” 10。

#### **3.2.3 炮的机动性与位置**

炮在开局时，放置在中路（当头炮）具有极高的威慑力，因此 PST 在开局阶段会给予中路位置加分。而在底线（巡河）的炮也有防守价值。但炮在空旷的区域（无炮架）价值会降低。这通常结合**动态评估**（Dynamic Evaluation）来调整，单靠静态 PST 难以完全描述炮的特性 21。

### **3.3 增量更新（Incremental Updates）：速度的关键**

如果每走一步（MakeMove）都要重新扫描全棋盘 32 个棋子来查表求和，计算量太大。
引擎采用增量更新技术：

* 初始化时计算全盘分数 Score。
* 当红马从 $A$ 点跳到 $B$ 点时：

    $$\text{NewScore} = \text{Score} - \text{PST}_{\text{Horse}}[A] + \text{PST}_{\text{Horse}}[B]$$
* 如果吃掉了黑卒：

  $$\text{NewScore} = \text{NewScore} - (\text{Material}_{\text{Pawn}} + \text{PST}_{\text{Pawn}}[\text{CapturedPos}])$$

  这种操作是 $O(1)$ 的，极大地提升了搜索速度 9。

### **3.4 锥形评估（Tapered Evaluation）：动态的价值表**

游戏从开局进入残局，棋子的价值是浮动的。

* **过河卒：** 开局时少见，残局时价值连城。
* **缺士象：** 开局影响不大，残局时缺士怕双车，缺象怕双炮。

为了解决这个问题，现代引擎（如 Stockfish 移植版、Pikafish）不使用单一的价值表，而是使用两套表：

1. **中局表 (MG Table)：** 关注出子速度、控制河口。
2. **残局表 (EG Table)：** 关注兵的推进、老将的安全性。

最终评分通过一个 **相位因子（Phase Factor）**进行线性插值：

$$ \text{FinalScore} = \frac{\text{MG\_Score} \times \text{Phase} + \text{EG\_Score} \times (256 - \text{Phase})}{256} $$

其中 Phase 根据棋盘上剩余大子（车马炮）的数量动态计算。这使得引擎能平滑地从进攻模式过渡到残局模式 5。

---

**4\. 搜索增强与剪枝策略**

在 Alpha-Beta 和价值表的基础上，成熟的象棋引擎还引入了多种技术来应对特定问题，特别是“水平线效应”和搜索爆炸。

### **4.1 静态搜索（Quiescence Search / Q-Search）**

Alpha-Beta 搜索在达到预定深度（例如 8 层）时会强制停止并调用评估函数。但这会导致严重问题：

* **水平线效应（Horizon Effect）：** 假设第 8 层时，红车刚刚吃掉黑马，看似红方大优（+400分）。但如果在第 9 层黑炮可以打掉红车呢？简单的评估会忽略这步反击，导致引擎做出错误判断。

**解决方案：** 当到达最大深度时，不立即评估，而是进入“静态搜索”。

* 在 Q-Search 中，**只搜索吃子着法（Captures）**。
* 直到局面“安静”下来（没有激烈的吃子交换），才调用价值表进行评估。
* 在中国象棋中，Q-Search 甚至需要包含“解将”着法，因为连杀是象棋战术的核心 17。

### **4.2 Delta 剪枝（Delta Pruning）**

在 Q-Search 中，由于只考虑吃子，分支依然可能很多。Delta 剪枝利用价值表进行快速判断：

* 如果 当前评估分 \+ 被吃子力的价值 \+ 安全余量(Delta) 依然小于 Alpha，那么这个吃子完全没有必要搜，因为它即便吃到了子也挽回不了劣势。
* 这在象棋中非常有用，例如：红方大劣（-800分），现在红车可以吃一个黑卒（+100分）。即便吃了，分数（-700）依然远低于 Alpha，因此可以直接剪枝 24。

### **4.3 空着裁剪（Null Move Pruning）**

引擎尝试“不走棋”（把出牌权直接交给对方）。如果即便我不走棋，评估分数依然高于 Beta（发生剪枝），说明我的局面优势极大，甚至不需要这一步棋也能守住。那么这个分支可以直接剪掉，从而节省大量时间。

* **注意：** 在象棋残局（如困毙局面 Zugzwang）中，空着裁剪可能导致误判，因此通常在残局阶段关闭或减弱此功能 25。

---

**5\. 中国象棋特有的算法挑战：规则与哈希**

与国际象棋不同，中国象棋的规则对算法提出了特殊要求，主要体现在**重复局面判决**和**Zobrist 哈希**的设计上。

### **5.1 复杂的“长打”判例**

国际象棋中，三次重复即和棋。但中国象棋规则极其复杂：

* **长将（Perpetual Check）：** 禁止。如果一方不停将军，必须变着，否则判负。
* **长捉（Perpetual Chase）：** 禁止。如果一方不停捉吃无根子（车/马/炮），判负。
* **一将一捉：** 通常允许，或者是复杂的循环规则。

算法实现：
引擎必须维护一个历史局面栈。在搜索树的每一个节点，检查当前局面是否在历史中出现过。

* 如果出现重复，不仅要返回“重复”标记，还必须调用一个专门的 RuleArbiter（裁决器）函数。
* 该函数回溯历史着法，分析是“长将”还是“长捉”。
* 如果是长将，给该分支返回一个极低的分数（负无穷），迫使引擎放弃这个导致长将的走法（即 Alpha-Beta 中的 Beta 剪枝逻辑会生效，或者 Alpha 不会更新） 26。

### **5.2 Zobrist 哈希与大棋盘**

置换表（Transposition Table）需要一个 64 位的哈希键（Key）来唯一标识局面。
由于象棋棋盘有 90 个点，且有红黑两方，Zobrist 数组的大小通常初始化为 2 sides \* 7 pieces \* 90 squares。

* **增量哈希：** 与价值表类似，哈希键也是在 MakeMove 时通过异或（XOR）操作增量更新的，保证了 $O(1)$ 的效率。
* **哈希冲突：** 即使是 64 位哈希，在 $10^{50}$ 的状态空间中也理论上存在冲突，但在实际工程中几乎可以忽略，或者通过存储校验码（Check Sum）来解决 11。

---

**6\. 从手工特征到神经网络：评估函数的演变**

### **6.1 手工调优与自动化调参 (CLOP/Texel)**

在 2010 年代之前，价值表中的数值（如马=4，车=9）多由程序员凭经验设定。后来出现了 **Texel Tuning** 等自动化调参技术。

* **原理：** 让引擎自我对弈数百万盘，或者分析人类大师的对局。
* **优化：** 使用逻辑回归或梯度下降，微调价值表中的每一个参数（例如，发现马在底线的价值其实是 3.8 而不是 4）。这使得价值表极其精确 5。

### **6.2 NNUE：价值表的终结？**

近年来，随着 **NNUE (Efficiently Updatable Neural Networks)** 技术的引入（首见于 Shogi，后被 Stockfish 和 Pikafish 采纳），传统的价值表正在被取代。

* **架构：** NNUE 实际上是一个巨大的、稀疏的神经网络。它的输入层直接映射棋盘特征（类似高级的价值表）。
* **优势：** 传统价值表是线性的（马的价值+车的价值）。NNUE 捕捉了**非线性特征**（例如：当缺象时，对方双马的价值指数级上升）。
* **结合：** 即使是 NNUE 引擎，依然使用 Alpha-Beta 进行搜索。NNUE 仅仅是替换了 Evaluate() 函数中的查表逻辑，但由于使用了 SIMD 指令集加速，其推断速度极快，并未拖累搜索深度 25。

---

**7\. 结论**

总结而言，Alpha-Beta 剪枝与价值表在中国象棋算法中扮演着决策大脑与直觉感知的角色。

1. **Alpha-Beta** 通过数学上的剪枝逻辑，使得引擎能够在 $10^{50}$ 状态空间的迷雾中，建立起一条通往最优解的确定性路径。着法排序（Move Ordering）是其效率的倍增器。
2. **价值表（PST）** 则是将象棋大师的千年智慧固化为矩阵数据。它通过静态的子力与位置评分，为搜索树的叶子节点提供锚点。增量更新与锥形评估技术保证了其在毫秒级时间内的准确性与动态性。

从早期的 ElephantEye 到现在的 Pikafish，尽管评估函数已从简单的二维数组进化为千万参数的神经网络，但 Alpha-Beta 搜索框架依然屹立不倒，证明了这一经典算法在博弈领域的永恒价值。对于开发者而言，理解这两者的协同——即**如何让搜索更深（剪枝效率）与如何让评估更准（价值表精度）**——是构建强力象棋引擎的不二法门。

#### **Works cited**

1. Chinese Chess \- Chessprogramming wiki, accessed December 17, 2025, [https://www.chessprogramming.org/Chinese\_Chess](https://www.chessprogramming.org/Chinese_Chess)
2. Mastering Chinese Chess AI(Xiangqi) Without Search \- arXiv, accessed December 17, 2025, [https://arxiv.org/html/2410.04865v1](https://arxiv.org/html/2410.04865v1)
3. AI Agent for Chinese Chess, accessed December 17, 2025, [http://stanford.edu/\~dengl11/resource/doc/221-Report.pdf](http://stanford.edu/~dengl11/resource/doc/221-Report.pdf)
4. (PDF) Tree Search Algorithms For Chinese Chess \- ResearchGate, accessed December 17, 2025, [https://www.researchgate.net/publication/363182984\_Tree\_Search\_Algorithms\_For\_Chinese\_Chess](https://www.researchgate.net/publication/363182984_Tree_Search_Algorithms_For_Chinese_Chess)
5. Wukong JS \- Chessprogramming wiki, accessed December 17, 2025, [https://www.chessprogramming.org/Wukong\_JS](https://www.chessprogramming.org/Wukong_JS)
6. xqbase/eleeye: ElephantEye \- a XiangQi (Chinese Chess) Engine for XQWizard with Strong AI \- GitHub, accessed December 17, 2025, [https://github.com/xqbase/eleeye](https://github.com/xqbase/eleeye)
7. Alpha–beta pruning \- Wikipedia, accessed December 17, 2025, [https://en.wikipedia.org/wiki/Alpha%E2%80%93beta\_pruning](https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning)
8. Alpha-Beta \- Chessprogramming wiki, accessed December 17, 2025, [https://www.chessprogramming.org/Alpha-Beta](https://www.chessprogramming.org/Alpha-Beta)
9. Piece-Square Tables \- Chessprogramming wiki, accessed December 17, 2025, [https://www.chessprogramming.org/Piece-Square\_Tables](https://www.chessprogramming.org/Piece-Square_Tables)
10. Piece-Square Tables \- Creating the Rustic chess engine, accessed December 17, 2025, [https://rustic-chess.org/evaluation/psqt.html](https://rustic-chess.org/evaluation/psqt.html)
11. Transposition Table, History Heuristic, and other Search Enhancements, accessed December 17, 2025, [https://homepage.iis.sinica.edu.tw/\~tshsu/tcg/2023/slides/slide8.pdf](https://homepage.iis.sinica.edu.tw/~tshsu/tcg/2023/slides/slide8.pdf)
12. Help with transposition table \- TalkChess.com, accessed December 17, 2025, [https://talkchess.com/viewtopic.php?t=83222](https://talkchess.com/viewtopic.php?t=83222)
13. Alpha-Beta pruning in Adversarial Search Algorithms \- GeeksforGeeks, accessed December 17, 2025, [https://www.geeksforgeeks.org/artificial-intelligence/alpha-beta-pruning-in-adversarial-search-algorithms/](https://www.geeksforgeeks.org/artificial-intelligence/alpha-beta-pruning-in-adversarial-search-algorithms/)
14. Beginner's Guide to Alpha-Beta Pruning: From Minimax to AI \- ProjectPro, accessed December 17, 2025, [https://www.projectpro.io/article/alpha-beta-pruning-in-ai/1157](https://www.projectpro.io/article/alpha-beta-pruning-in-ai/1157)
15. Alpha Beta Pruning in AI \- Great Learning, accessed December 17, 2025, [https://www.mygreatlearning.com/blog/alpha-beta-pruning-in-ai/](https://www.mygreatlearning.com/blog/alpha-beta-pruning-in-ai/)
16. An Update on Game Tree Research Tutorial 3: Alpha-Beta Search and Enhancements, accessed December 17, 2025, [https://webdocs.cs.ualberta.ca/\~mmueller/courses/2014-AAAI-games-tutorial/slides/AAAI-14-Tutorial-Games-3-AlphaBeta.pdf](https://webdocs.cs.ualberta.ca/~mmueller/courses/2014-AAAI-games-tutorial/slides/AAAI-14-Tutorial-Games-3-AlphaBeta.pdf)
17. Quiescence Search \- Chessprogramming wiki, accessed December 17, 2025, [https://www.chessprogramming.org/Quiescence\_Search](https://www.chessprogramming.org/Quiescence_Search)
18. Delta pruning problem \- Chess Stack Exchange, accessed December 17, 2025, [https://chess.stackexchange.com/questions/46619/delta-pruning-problem](https://chess.stackexchange.com/questions/46619/delta-pruning-problem)
19. The Value of the Pieces in Xiangqi (Chinese Chess), accessed December 17, 2025, [https://www.xiangqi.com/articles/the-value-of-the-pieces-in-xiangqi-chinese-chess](https://www.xiangqi.com/articles/the-value-of-the-pieces-in-xiangqi-chinese-chess)
20. Matrix representation of piece position for a chess engine, accessed December 17, 2025, [https://chess.stackexchange.com/questions/8949/matrix-representation-of-piece-position-for-a-chess-engine](https://chess.stackexchange.com/questions/8949/matrix-representation-of-piece-position-for-a-chess-engine)
21. How To Play Chinese Chess (Xiangqi)\!, accessed December 17, 2025, [https://www.chess.com/blog/SamCopeland/how-to-play-chinese-chess](https://www.chess.com/blog/SamCopeland/how-to-play-chinese-chess)
22. Xiangqi \- Wikipedia, accessed December 17, 2025, [https://en.wikipedia.org/wiki/Xiangqi](https://en.wikipedia.org/wiki/Xiangqi)
23. Evaluation \- Chessprogramming wiki, accessed December 17, 2025, [https://www.chessprogramming.org/Evaluation](https://www.chessprogramming.org/Evaluation)
24. Delta Pruning \- Chessprogramming wiki, accessed December 17, 2025, [https://www.chessprogramming.org/Delta\_Pruning](https://www.chessprogramming.org/Delta_Pruning)
25. danieltan1517/orange-xiangqi: Chinese Chess AI \+ UI. Uses NNUE. Perfectly handles all AXF repetition rules. \- GitHub, accessed December 17, 2025, [https://github.com/danieltan1517/orange-xiangqi](https://github.com/danieltan1517/orange-xiangqi)
26. \[Revue de papier\] Complete Implementation of WXF Chinese Chess ..., accessed December 17, 2025, [https://www.themoonlight.io/fr/review/complete-implementation-of-wxf-chinese-chess-rules](https://www.themoonlight.io/fr/review/complete-implementation-of-wxf-chinese-chess-rules)
27. Xiangqi chase algorithm \- TalkChess.com, accessed December 17, 2025, [https://talkchess.com/viewtopic.php?t=41110](https://talkchess.com/viewtopic.php?t=41110)
28. Comparison Training for Computer Chinese Chess \- arXiv, accessed December 17, 2025, [https://arxiv.org/pdf/1801.07411](https://arxiv.org/pdf/1801.07411)
29. official-pikafish/px0: Open source neural network xiangqi engine with GPU acceleration and broad hardware support. \- GitHub, accessed December 17, 2025, [https://github.com/official-pikafish/px0](https://github.com/official-pikafish/px0)
30. arXiv:2412.17948v1 \[cs.AI\] 23 Dec 2024, accessed December 17, 2025, [https://arxiv.org/pdf/2412.17948](https://arxiv.org/pdf/2412.17948)