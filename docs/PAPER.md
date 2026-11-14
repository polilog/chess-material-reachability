# On the Sufficiency of Tomic's Criterion for Reachable Chess Material Configurations

**Author:** Kanstantsin Palitai  
**Research and computational assistance:** OpenAI ChatGPT (GPT-6)  
**Version:** 1.0.0

## Abstract

A material configuration of standard chess specifies only the multiplicities of the six piece types of each color, including both kings, and disregards the squares occupied. Ratko Tomic's 1999 constraints, as recorded by Kirill Kryukov, admit 29,045,304 such configurations up to color interchange. This count is well known as a combinatorial enumeration, but the reverse implication from material constraints to reachability requires legal histories. We give a self-contained proof of the necessity of Tomic's inequalities, a compact independent calculation of the candidate count, and a computer-assisted approach to sufficiency based on legal proof games and symbolic families. A single parameterized certificate can represent many independent promotion choices, and a storage certificate can additionally support many independent deletions of material. The recorded full cold replay attains the candidate count for every size from two through 32 pieces. We provide the original move-level evidence, checkers, and a cold-replay protocol that recomputes coverage from the certificates without trusting prior coverage matrices. The theorem is computational, rather than an enumeration of all possible chess positions or a purely analytic constructive theorem. The status of earlier sufficiency proofs and the independent validation of this publication should be distinguished from the known numerical count.

## 1. Problem and definitions

We use the ordinary initial position and the FIDE Laws of Chess [1]. Both kings are always present. A side profile is a vector

$$
s=(P,N,B,R,Q)\in\mathbb{Z}_{\ge0}^{5}.
$$

The two-sided material configuration is an unordered pair of side profiles $\{s_W,s_B\}$; interchanging White and Black gives the same configuration for counting purposes. Its size is $n=2+\sum_i s_{W,i}+\sum_i s_{B,i}$. The term *piece* includes a pawn and either king in this paper. Bishops are not distinguished by square color in the profile, though the witness must obey the actual rules of bishop movement. We do not distinguish side to move, castling rights, en passant rights, or other positional information.

A configuration is **reachable** if there exists a legal finite history from the standard initial position whose board has this profile. A terminal position is permitted as the last position. A witness cannot pass through an earlier terminal position. In particular, automatic fivefold repetition, the 75-move rule, stalemate, checkmate and dead positions must be respected. Draws by agreement, resignation, time forfeits, and optional draw claims need not occur in an existential witness. The supplied proofs use cooperative, not necessarily optimal, play.

Let $R_n$ denote the reachable configurations of size $n$, and $T_n$ the candidate configurations defined below. The target assertion is

$$
R_n=T_n\qquad(2\le n\le32).
$$

This is a statement about **material profiles**, not a claim that every arrangement of an admissible multiset of pieces is legal or reachable, and not a tablebase solution. It also does not assert the existence of a shortest proof game for each profile.

## 2. Prior work and scope of novelty

Kryukov's *Counting chess endgames* [2] distinguishes generalized chess, arbitrary-starting-position chess and standard chess. The standard-chess table attributes the material restrictions to Tomic [3,4]. The candidate numbers in this paper reproduce that table, not a new numerical sequence. Havermann's 1999 combinatorial work, cited by Kryukov, treats a less restrictive counting problem; the generalized count for $n$ pieces is the color-interchange quotient of weak compositions of $n-2$ into ten slots. It agrees with the standard count only at sufficiently small $n$.

The 2022 TalkChess discussion *Number of unique piece counts in chess* [5] revisits single-side counts including promotions. The resulting 8,694 one-side profiles alone do not establish simultaneous reachability of the two sides. The 2014 Chess Stack Exchange question [6] asks a related question with piece counts pooled across colors; its object of enumeration is not the same unordered pair used here.

Gourion [7] studies upper bounds on diagrams with no promotions, using classes of pawn arrangements. Tromp and Österlund's ChessPositionRanking project [8] addresses the much larger problem of reachability and counting particular board positions and uses concrete proof games and retrograde constraints. These are useful methodological precedents, not proofs of the material-profile theorem presented here. See also the Texel proof-game documentation [9].

The numerical result and criterion are due to Tomic and Kryukov's exposition. Our potential contribution is an explicit certificate-based demonstration that the material conditions are sufficient, using parameterized promotions and deletions. **We make no claim of being the first to prove sufficiency.** The full texts of Tomic's two 1999 forum messages could not be recovered during the literature search; [2] cites them but does not supply the complete constructive proof needed here. A direct inquiry to the authors and independent external reproduction are desirable before making stronger priority claims. See [RELATED_WORK.md](RELATED_WORK.md) for precise references and retrieval limitations.

## 3. Tomic's necessary conditions: a self-contained proof

Write the initial nonpawn, nonking vector as $o=(2,2,2,1)$ in the order $N,B,R,Q$. For a profile $s$, set

$$
u(s)=\sum_{i\in\{N,B,R,Q\}}(s_i-o_i)_+,\qquad d(s)=8-P-u(s),
$$

$$
\ell(s)=15-\sum_i s_i,
$$

where $(x)_+=\max(x,0)$. The quantity $u$ is the minimum number of promotions required to account for the final nonpawn surplus. The quantity $d$ is an upper bound on the number of original pawns captured *while still pawns*, not a claim about the actual history. The quantity $\ell$ is the exact number of pieces lost by the side because each promotion preserves total material count. The total number of captures is $C=\ell_W+\ell_B=32-n$.

**Theorem 1 (necessity).** Every reachable material configuration satisfies, for each side, $\ell\ge0$ and $d\ge0$, and the following inequalities (1):

$$
u_W\le C+d_B,\qquad u_B\le C+d_W.
$$

**Proof.** Let $a_W,a_B$ be the actual numbers of promotions along the witnessing history, including promotions whose descendants are subsequently captured. Let $D_W,D_B$ be the actual numbers of original pawns captured before promotion. Each original pawn has exactly one of three fates at the observed position: remains a pawn, has been captured as a pawn, or has promoted. Thus $P+a+D=8$. A nonpawn surplus can arise only through promotions, so $a\ge u$. Consequently $D=8-P-a\le d$ and $d\ge0$. The fact that captures are the only events reducing the number of pieces on the board gives $\ell\ge0$ and $C=\ell_W+\ell_B$.

We establish $a_W\le C+D_B$ by charging every promoted white pawn to a capture event. Label the sixteen original pawns by their original files. For each promoted white pawn:

1. If it made any capture before or at promotion, charge its first such capture. This includes en passant and a capturing promotion.
2. Otherwise it stayed on its original file until promotion. The original black pawn on that file must have either made a capture leaving the file, or have been captured while still a pawn. Charge the first such event. If neither event occurred, both original pawns would remain on the same file while both were unpromoted; their vertical order could not reverse under forward-only moves into unoccupied squares, so the white pawn could not reach rank eight. The black pawn also cannot first promote straight past that white pawn without one of the stated events.

In case 1 different white pawns charge distinct captures. In case 2 different white pawns correspond to different original black pawns. A capture is charged at most once in its capacity as a departure by a pawn: the capturing pawn belongs to exactly one color, so it cannot be both a white departure from case 1 and a black departure from case 2. It can additionally be charged at most once as the removal of a black pawn. The number of events with that extra capacity is at most $D_B$. It follows that the total number of charged promotions is at most $C+D_B$. Using $u_W\le a_W$ and $D_B\le d_B$ proves the first inequality of (1). Interchanging colors in the argument proves the other inequality. ∎

This proof does not assume that the minimum-promotion history is the actual history. It permits promotions followed by capture, en passant, and arbitrary interleaving of captures and promotions. It also proves that the conditions are necessary even if we disregard automatic draws; respecting those draws only restricts reachability further.

**Example.** At $n=32$, $C=0$. There have been no captures, so the charge argument forces no promotions. The initial material is the unique admissible profile. At $n=31$, one capture can unblock up to two white promotions and one black promotion if the victim is a black pawn; the reverse orientation is analogous. The certificate corpus contains witnesses for all 155 candidate profiles at that size.

## 4. Independent enumeration of the upper bound

An admissible side profile satisfies $0\le P\le8$, $0\le N,B,R\le10$, $0\le Q\le9$, $\ell\ge0$, and $d\ge0$. These ranges follow from the initial material plus at most eight promotions. There are 8,694 such profiles. Group them by the triple $(\ell,u,d)$, and let $g(\ell,u,d)$ denote the number in a group. There are 324 nonempty groups.

For two groups $g,h$, with parameters $(\ell,u,d)$ and $(\ell',u',d')$, the compatibility test is

$$
u\le\ell+\ell'+d',\qquad u'\le\ell+\ell'+d.
$$

All profiles in the same pair of groups have equal total size $32-\ell-\ell'$ and the same compatibility status. The contribution of two distinct compatible groups is $g h$; the contribution of a compatible group with itself is $g(g+1)/2$. Therefore summing over unordered pairs of groups gives $|T_n|$ without a search over chess histories or all individual two-sided candidates. The reference implementation `src/upper_bound.py` independently generates the single-side profiles and applies this formula using exact integer arithmetic. The computation can also be expressed through the generating function

$$
\sum_{s:\ell,d\ge0} x^{\ell(s)} y^{u(s)}z^{d(s)},
$$

whose coefficients are the group multiplicities.

The total is $\sum_n|T_n|=29,045,304$. There are 6,298 compatible diagonal profiles $(s,s)$, so the number of oriented candidates, if colors are distinguished, is $2\cdot29,045,304-6,298=58,084,310$. The present sufficiency claim concerns the **unordered** profiles; one may not infer oriented reachability merely by swapping colors in a history starting with White to move. An additional argument or orientation-specific verification would be needed for that stronger claim.

The known per-size candidate counts and the recorded cumulative verification are supplied in `results/expected.tsv`. They are also listed here.

| Pieces | Candidates | Recorded covered |
|---:|---:|---:|
| 2 | 1 | 1 |
| 3 | 5 | 5 |
| 4 | 30 | 30 |
| 5 | 110 | 110 |
| 6 | 365 | 365 |
| 7 | 1,001 | 1,001 |
| 8 | 2,520 | 2,520 |
| 9 | 5,720 | 5,720 |
| 10 | 12,190 | 12,190 |
| 11 | 24,309 | 24,309 |
| 12 | 46,233 | 46,233 |
| 13 | 83,817 | 83,817 |
| 14 | 146,094 | 146,094 |
| 15 | 244,350 | 244,350 |
| 16 | 393,114 | 393,114 |
| 17 | 606,777 | 606,777 |
| 18 | 899,592 | 899,592 |
| 19 | 1,279,689 | 1,279,689 |
| 20 | 1,749,075 | 1,749,075 |
| 21 | 2,294,793 | 2,294,793 |
| 22 | 2,889,021 | 2,889,021 |
| 23 | 3,477,150 | 3,477,150 |
| 24 | 3,980,871 | 3,980,871 |
| 25 | 4,243,148 | 4,243,148 |
| 26 | 3,783,484 | 3,783,484 |
| 27 | 2,178,319 | 2,178,319 |
| 28 | 613,655 | 613,655 |
| 29 | 83,625 | 83,625 |
| 30 | 6,090 | 6,090 |
| 31 | 155 | 155 |
| 32 | 1 | 1 |
| Total | 29,045,304 | 29,045,304 |

## 5. Constructive lower bound: proof games and symbolic certificates

Theorem 1 proves $R_n\subseteq T_n$. To prove the reverse inclusion, we supply witnesses and a verifier which credits only configurations justified by a legal history. The proof is computer-assisted: it does not require constructing every possible placement of a material multiset, and it does not require solving any game. It does check finite move-level certificates and exact set coverage.

### 5.1 Ordinary witnesses and intermediate profiles

A witness consists of UCI coordinate moves starting from the standard board. A concrete checker tests piece geometry, obstruction of sliding moves, capture legality, pawn moves, promotions, and king safety after each move; it checks the automatic repetition and halfmove limits. Our concrete checker supports en passant and checks it at the final mate test; no castling is needed by accepted witness lines. The final position is certified as checkmate. All earlier positions are non-dead, because the verified continuation demonstrates a possible mate. Stalemate or an earlier checkmate cannot have a legal next move. Hence a verified mating game certifies every material profile along it, including every material-changing prefix. A terminal target with no possible mate is handled separately: a branch from a non-dead prefix reaches the terminal target, while a different verified continuation to mate proves the common prefix non-dead. The final capture is independently verified. This avoids the invalid argument that K vs K could be reached by continuing after K+N vs K.

### 5.2 Independent promotion choices and branch joining

In symbolic certificates, an unknown promoted piece $X$ has a specified finite domain $D\subseteq\{N,B,R,Q\}$. It is stationary during common moves. Its possible attacks are conservatively bounded by the union of the attacks of its allowed types. For a domain containing all four, this is the union of queen and knight attacks. Every possible type has identical occupancy and color. A common move is accepted only if it is legal for this conservative attack model. A `PROM` instruction checks every permitted promotion; a `PARK` or `SHIFT` instruction gives type-specific short routes, with an exact rejoin of occupancy and side to move. No assertion that substituting a knight for a queen preserves arbitrary subsequent moves is needed.

**Lemma 2 (symbolic soundness).** Suppose a verified symbolic prefix represents all assignments to its independent domains, and each assignment has a legal realization of that prefix. A common legal move checked against the union of attacks preserves this invariant. A branch operation checked for each possible local type preserves it when the branch endpoints agree in symbolic occupancy, color, and side to move, and the verifier retains conservative bounds on history-dependent draw counters. Repeated application proves legality of every assignment represented at any accepted symbolic state.

**Proof.** Every exact attack is in the conservative union. Occupancy and color, and therefore all common fixed-piece paths and capture targets, agree across assignments. For a local type-dependent move, the active type is fixed while all other unknowns are still conservatively bounded. After the verified rejoin the inductive invariant holds for each combination of choices. For fivefold repetition, the verifier uses a coarser position signature (color occupancy and side to move), for which equality of exact positions implies equality of signatures. Bounding each signature's maximum count below five is sufficient. The maximum across branches is retained, not an average. The halfmove counter is exact or bounded above by the maximum among branches. An accepted common mating suffix is checked conservatively in the opposite direction: it must provide a check and forbid every possible escape. For optional-pawn domains, the stationary pawn is on rank six (White) or three (Black); its ordinary forward/capturing moves are contained in the queen's geometric moves at these squares, and it cannot castle, move two squares, or take en passant from them. The certificate language does not permit arbitrary movement of an unknown piece. The invariant and the mating continuation prove reachability of every credited intermediate profile. ∎

`REVEAL` specializes an existing choice to a concrete type; the implementation discards earlier unqualified families rather than falsely crediting choices that no longer have a verified continuation. `OPTION` allows a pawn to remain a pawn or return to a common square after one of four promotion choices, with separately checked routes. This increases coverage without requiring a proof of complete independence for every pawn on every file.

There is also a useful restricted generalization of ordinary mating games: track the identities of promoted pieces and restrict each captured descendant's domain by its actual moves and its attacks on the moving side's king. Surviving promoted pieces retain their original types at the final mate. Because alternative types preserve occupancy and color, the resulting domains are independent; attack exclusions and movement constraints are tested throughout. This is implemented by `src/symbolic_all.cpp` and permits many new material profiles from one concrete game. The overapproximate repetition signature is independent of these allowed types.

### 5.3 Independent deletion certificates

A storage certificate reaches a geometry with both kings and two designated service knights, plus a set of optional stationary pieces. Every stationary piece is checked not to attack the opposing king even on an otherwise empty board (using its allowed attack union). For each optional piece, a route of the opposite service knight captures it and returns, while the other service knight makes reversible waiting moves. The route avoids every other occupied square and does not give check to the opposite king. It is verified on the full storage board. The final occupancy differs only by deletion of the selected piece, with the same side to move. Since removing other stationary pieces cannot introduce an attack on either king under the empty-board condition, the operations remain valid after any subset of other removals.

**Lemma 3 (independent deletion).** If each deletion module preserves the stated storage invariant, and the repetition/halfmove bounds hold across successive modules, then any subset of optional stationary pieces can be deleted while retaining the core. A mating continuation from the core establishes non-deadness before the target. An optional service-knight sacrifice can be certified as a final alternative branch, provided a reversible round trip and a continuation to the core mate establish non-deadness up to that branch.

**Proof.** Induct on the number of removed pieces. No knight route needs an optional square except the intended victim, and removing a stationary piece only frees a square. The empty-board attack condition prevents discovery of a new slider attack on either king. A capture changes the number of occupied squares, so an exact repetition cannot cross the capture. Within a material-preserving interval, the verified core-position repetition bounds and maximum number of quiet plies apply to every permitted subset. The common core mate excludes dead positions. For a final sacrifice the verified reverse route is an alternative before the final capture, so the target need not itself be non-dead. ∎

This lemma does not assert that arbitrary subsets of an arbitrary reachable chess position are themselves reachable. Only verified storage geometries and routes have the required property. In particular, the main storage checker credits at most one service-knight sacrifice; it does not claim universal deletion of both helpers. The separate illustrative no-promotion certificate in `proof/` has additional terminal cases.

### 5.4 Finite coverage and exact set union

A verified snapshot describes two independent side families. A family signature encodes fixed counts $(P,N,B,R,Q)$ followed by symbolic slots with a nonempty domain. To expand a side, start with the fixed vector and add one unit vector for each slot, choosing its type from the domain. Repeated equal vectors are identified. The Cartesian product of the two side families consists entirely of reachable profiles by Lemma 2. Storage certificates describe downward-closed subfamilies subject to retaining service knights (or an explicitly certified final sacrifice), handled separately by Lemma 3.

The verifier adds each family to an exact finite coverage relation on the 8,694 side profiles. The cold replay uses an upper-triangular candidate matrix for ordinary and symbolic witnesses and bitsets for the deletion rectangles. It checks membership in the independently generated candidate relation, and compares the final relation with the full candidate relation, not just the total count. All coverage is deduplicated under color interchange. The initial position is an explicit zero-move witness. If the relations coincide, Theorem 1 and the soundness of the certificates imply equality of the reachable and candidate sets.

## 6. Results and reproducibility

The historical cumulative calculation reported equality for all sizes 2–32; the publication audit confirmed equality by replaying raw certificates rather than trusting previously saved coverage. The initial audit exposed 82 missing profiles caused by minimizing an earlier archive for size 26 alone; seven ordinary games and 28 symbolic templates were recovered and revalidated. A packaging regression involving an output filename collision was also corrected. In this consolidated edition, the historical archive chain is replaced by a selected, deduplicated corpus in `data/`, with the small terminal-target witnesses in `examples/small/`. The standalone `verify.py` replays the retained concrete, symbolic and storage certificates from scratch, derives their families and tests exact set equality against the candidate relation. No historical matrix or saved family output is trusted. See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for the protocol and `results/final_replay.log` for the fresh integrated-edition run (and `results/compact_replay.log` for the earlier standalone run).

**Theorem 2 (computer-assisted sufficiency).** Every unordered material profile satisfying the constraints in Theorem 1 is reachable. The proof uses the verified finite certificate computation, with the soundness conditions detailed in Section 5. In particular the number of reachable material configurations in standard chess is 29,045,304.

**Proof.** Theorem 1 gives $R\subseteq T$. Each credited entry belongs to $R$ by the concrete or symbolic legality arguments above. The full coverage calculation verifies that the union of those entries equals $T$. Hence $T\subseteq R$, proving equality and the count. The finite certificate calculation is an essential premise of the proof, not a substitute for the mathematical argument about certificate soundness. ∎

The consolidated corpus retains 309,421 ordinary game records, 66,473 parameterized template blocks, and 420 storage/deletion blocks, plus the small terminal-target witnesses. The subset was selected by crediting previously checked families and retaining certificates that added coverage; this selection heuristic is not used as proof of their validity. The standalone verifier independently replays the retained records and checks exact coverage. The corpus is sufficient, not asserted to be globally minimal. Search failure is not evidence of impossibility.

### 6.1 Illustrative certificates

The included PGN `examples/14_queens_game.pgn` reaches a board after Black's 129th move with nine white queens and five black queens, all 14 original nonking nonpawn pieces (including the original queens) and both kings retained, and no pawns. Four black pawns are captured; the other 12 original pawns promote. This is a useful test of the distinction between total material and type multiplicity. It is a synthetic proof game, not a historic competitive game. Compact independent-promotion, no-promotion deletion and promotion-plus-deletion examples are included under `proof/`. The much larger corpus establishes coverage, while these small examples illustrate the proof ideas without requiring millions of moves.

### 6.2 Limitations and future work

The result concerns unordered profiles and standard chess from the orthodox initial position. The code deliberately restricts some witness operations (e.g. no castling); this is sound for a lower-bound existence proof and does not claim the restricted language describes all games. We do not prove a purely analytic global construction, that any arbitrary layout is reachable, or a general monotonicity theorem for deleting pieces. We do not establish shortest witnesses. An independent implementation of the symbolic checker and an external cold replay would strengthen confidence. A purely mathematical proof that replaces the corpus by finitely many universally composable modules remains a separate desirable objective. The archived research contains intermediate conditional reductions and failed searches, not all of which are used in Theorem 2; the final proof relies on accepted move certificates and set equality, not on those conjectured reductions. A reported equality from a cached matrix must never be confused with a new full replay of its underlying witnesses.

## 7. AI assistance and responsibility

The human researcher directed the investigation and requested increasingly stringent verification and compact constructive arguments. OpenAI ChatGPT (GPT-6) assisted with mathematical reasoning, algorithm design, C++ and Python implementation, construction of games and certificates, computational experiments, and preparation of this manuscript. The software and archived evidence, rather than AI-generated assertions, are the verification mechanism. The human author should review the work and assume responsibility for its scientific claims. No external validation or peer review is implied.

## References

1. FIDE. *Laws of Chess*, effective 1 January 2023, especially Arts. 3, 5.2.2, 9.2.2 and 9.6. https://handbook.fide.com/chapter/E012023
2. Kirill Kryukov. *Counting chess endgames*. Updated 27 February 2025. https://kirill-kryukov.com/chess/counting-chess-endgames/
3. Ratko Tomic. *Counting & Encoding Any Chess Position in 157 bits*. Computer Chess Club, 9 November 1999. Cited in [2]; original archived URL: https://www.stmintz.com/ccc/index.php?id=77068 (full text not recovered).
4. Ratko Tomic. *Algorithm for Encoding Any Position in 155 bits (part 2/2)*. Computer Chess Club, 15 November 1999. Cited in [2]; original archived URL: https://www.stmintz.com/ccc/index.php?id=77859 (full text not recovered).
5. Daniel Infuehr, Uri Blass, H. G. Muller and other participants. *Number of unique piece counts in chess*. TalkChess, July 2022. https://talkchess.com/viewtopic.php?t=80375
6. Chess Stack Exchange contributors. *How many possible combinations for the number of pieces on the board?* 2014. https://chess.stackexchange.com/questions/4561/how-many-possible-combinations-for-the-number-of-pieces-on-the-board
7. Daniel Gourion. *An upper bound for the number of chess diagrams without promotion*. ICGA Journal 44(2), 2022. DOI: 10.3233/ICG-220210; arXiv:2112.09386. https://arxiv.org/abs/2112.09386
8. John Tromp and contributors (including Peter Österlund). *ChessPositionRanking*. https://github.com/tromp/ChessPositionRanking
9. Peter Österlund. *Texel proof game documentation*. https://github.com/peterosterlund2/texel/blob/master/doc/proofgame.md

All online sources consulted for the draft on 14 November 2026. See [RELATED_WORK.md](RELATED_WORK.md) for additional bibliographic notes.
