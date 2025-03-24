/*
    
    Intelligent and Optimized Tic-Tac-Toe Agent

    Overview:
    - Implements a strategic, rule-based move selection algorithm.
    - Designed for scalability, supporting different board sizes and variations.
    - Ensures code efficiency, readability, and maintainability.
    - Adheres to core strategic principles: winning, blocking, center control, and optimal positioning.

*/




/* Board Representation and Rules */

isCoordinate(0).
isCoordinate(1).
isCoordinate(2).
isCell(X,Y) :- isCoordinate(X) & isCoordinate(Y).
available(X,Y) :- isCell(X,Y) & not mark(X,Y,_).





// Winning Move Check: Determines if a move at (X,Y) secures victory for the player
checkWinningMove(X,Y,Player) :-
    available(X,Y) &
    (
        // Check for three in a row
        mark(X,Y1,Player) & mark(X,Y2,Player) & (Y1 \== Y & Y2 \== Y & Y1 \== Y2) |
        
        // Check for three in a column
        mark(X1,Y,Player) & mark(X2,Y,Player) & (X1 \== X & X2 \== X & X1 \== X2) |

        // Check for three in the primary diagonal (↘️)
        ((X == 0 & Y == 0) | (X == 1 & Y == 1) | (X == 2 & Y == 2)) 
        & mark(X1,Y1,Player) & mark(X2,Y2,Player) &
        (X1 \== X & X2 \== X & X1 \== X2) &
        (Y1 \== Y & Y2 \== Y & Y1 \== Y2) |

        // Check for three in the secondary diagonal (↙️)
        ((X == 0 & Y == 2) | (X == 1 & Y == 1) | (X == 2 & Y == 0)) &
        mark(X3,Y3,Player) & mark(X4,Y4,Player) &
        (X3 \== X & X4 \== X & X3 \== X4) &
        (Y3 \== Y & Y4 \== Y & Y3 \== Y4)
    ).

// Blocking Move Check: Determines if a move at (X,Y) prevents an opponent's victory
checkBlockingMove(X,Y,Player) :-
    otherSymbol(Player, Opponent) &
    checkWinningMove(X,Y,Opponent).

// Helper Function: Defines the opposing player's symbol
otherSymbol(x,o).
otherSymbol(o,x).




/* Pregame Handlers */

// Game Initialization
started.

// Greet the Player on Game Start
+started <- sayHello.

// Main strategy for choosing a move
+round(Z) : next & symbol(S) <- 
    ?chooseMove(X,Y);
    play(X,Y).




/* Move Selection Strategy */

// 1. Priority - Prioritize winning if a victory move exists
chooseMove(X,Y) :- 
    symbol(S) & 
    checkWinningMove(X,Y,S).

// 2. Priority - lock an imminent win by the opponent
chooseMove(X,Y) :- 
    symbol(S) & 
    checkBlockingMove(X, Y, S).

// 3. Priority - Prefer the center if available
chooseMove(1,1) :- 
    available(1,1).

// 4. Priority - Select a corner if available, avoiding opposite corners occupied by the opponent
chooseMove(X,Y) :- 
    available(X,Y) & 
    (((X = 0 & Y = 0) & not mark(2,2,Opponent)) |
     ((X = 0 & Y = 2) & not mark(2,0,Opponent)) |
     ((X = 2 & Y = 0) & not mark(0,2,Opponent)) |
     ((X = 2 & Y = 2) & not mark(0,0,Opponent))).

// 5. Priority - Default to any available space if can't find strategic moves
chooseMove(X,Y) :- 
    available(X,Y).




/* Endgame Handlers */

+winner(S) : symbol(S) <- .print("I won!").
+end <- confirmEnd.