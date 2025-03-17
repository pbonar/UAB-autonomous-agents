/* 
    Uses Current Priority-Based Strategy:
    (+) Computationally simpler and faster
    (+) Very effective at immediate tactical moves (winning moves and blocking)
    (+) Never makes obvious mistakes
    (+) Follows basic strategic principles (control center, take cor    ners)
    (-) Can't plan multiple moves ahead
    (-) Might miss winning sequences that require setup
    (-) Could be predictable in certain positions
    (-) May not always choose the optimal move when no immediate threat exists
*/

/* Initial beliefs and rules */
isCoordinate(0).
isCoordinate(1).
isCoordinate(2).
isCell(X,Y) :- isCoordinate(X) & isCoordinate(Y).
available(X,Y) :- isCell(X,Y) & not mark(X,Y,_).

// Check winning positions
canWin(X, Y, Player) :- 
    available(X,Y) & 
    checkWinningMove(X,Y,Player).

// Check if a move at (X,Y) would create a win for Player
checkWinningMove(X,Y,Player) :-
    available(X,Y) &
    (
        // Check row
        mark(X,Y1,Player) & mark(X,Y2,Player) & (Y1 \== Y & Y2 \== Y & Y1 \== Y2) |
        // Check column
        mark(X1,Y,Player) & mark(X2,Y,Player) & (X1 \== X & X2 \== X & X1 \== X2) |
        // Check diagonals
        mark(X1, Y1, Player) & mark(X2, Y2, Player) & (X1 \== X & X2 \== X & X1 \== X2) & (Y1 \== Y & Y2 \== Y & Y1 \== Y2) |
		mark(X1, Y1, Player) & mark(X2, Y2, Player) & (X1 \== X & X2 \== X & X1 \== X2) & (Y1 \== Y & Y2 \== Y & Y1 \== Y2)
    ).

started.

/* Plans */
+started <- sayHello.

// Main strategy for choosing a move
+round(Z) : next & symbol(S) <- 
    ?chooseMove(X,Y);
    play(X,Y).

/* Strategic move selection */
// First priority: Win if possible
chooseMove(X,Y) :- 
    symbol(S) & 
    canWin(X, Y, S).

// Second priority: Block opponent's win
chooseMove(X,Y) :- 
    symbol(S) & 
    otherSymbol(S,OS) & 
    canWin(X, Y, OS).

// Third priority: Take center if available
chooseMove(1,1) :- 
    available(1,1).

// Fourth priority: Take a corner if available
chooseMove(X,Y) :- 
    available(X,Y) & 
    ((X = 0 & Y = 0) |
     (X = 0 & Y = 2) |
     (X = 2 & Y = 0) |
     (X = 2 & Y = 2)).

// Last priority: Take any available space
chooseMove(X,Y) :- 
    .findall(available(A,B), available(A,B), AvailableCells) &
    .length(AvailableCells, L) &
    L > 0 &
    .nth(0, AvailableCells, available(X,Y)).

// Helper rule to get opponent's symbol
otherSymbol(x,o).
otherSymbol(o,x).

/* Required end game handlers */
+winner(S) : symbol(S) <- .print("I won!").
+end <- confirmEnd.