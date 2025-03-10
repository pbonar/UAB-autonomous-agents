
/*

Implementation of a Tic-Tac-Toe player that just plays random moves.

When the agent is started it must first perform a 'sayHello' action.
Once all agents have done this, the game or tournament starts.

Each turn the agent will observe the following percepts:

- symbol(x) or symbol(o) 
	This indicates which symbol this agent should use to mark the cells. It will be the same in every turn.

- a number of marks:  e.g. mark(0,0,x) , mark(0,1,o) ,  mark(2,2,x)
  this indicates which cells have been marked with a 'x' or an 'o'. 
  Of course, in the first turn no cell will be marked yet, so there will be no such percept.

- round(Z)
	Indicates in which round of the game we are. 
	Since this will be changing each round, it can be used by the agent as a trigger to start the plan to determine
	its next move.

Furthermore, the agent may also observe the following:

- next 
	This means that it is this agent's turn.
  
- winner(x) or winner(o)
	If the game is over and did not end in a draw. Indicates which player won.
	
- end 
	If the game is finished.
	
- After observing 'end' the agent must perform the action 'confirmEnd'.

To mark a cell, use the 'play' action. For example if you perform the action play(1,1). 
Then the cell with coordinates (1,1) will be marked with your symbol. 
This action will fail if that cell is already marked.

*/



/* Initial beliefs and rules */


// First, define a 'cell' to be a pair of numbers, between 0 and 2. i.e. (0,0) , (0,1), (0,2) ... (2,2).

isCoordinate(0).
isCoordinate(1).
isCoordinate(2).

isCell(X,Y) :- isCoordinate(X) & isCoordinate(Y).

/* A cell is 'available' if it does not contain a mark.*/
available(X,Y) :- isCell(X,Y) & not mark(X,Y,_).

/* We also define what cells are corners */
corner(0,0).
corner(0,2).
corner(2,0).
corner(2,2).

/* Definition of what a winning sequence looks like */
win(X,Y) :- mySymbol(S) & completesLine(X,Y,S).

completesLine(X,Y,S) :- twoInRow(X,Y,S). /* Check if there is a row of two */
completesLine(X,Y,S) :- twoInCol(X,Y,S). /* Check if there is a column of two */
completesLine(X,Y,S) :- twoInDiag(X,Y,S). /* Check if there is a diagonal of two */

twoInRow(X,Y,S) :- mark(X,Y1,S) & mark(X,Y2,S) & Y\==Y1 & Y\==Y2.
twoInCol(X,Y,S) :- mark(X1,Y,S) & mark(X1,Y,S) & X\==X1 & X\==X2.
twoInDiag(X,Y,S) :- (mark(X1,Y1,S) & mark(X2,Y2,S) & X \== X1 & X \== X2 & Y \== Y1 & Y \== Y2 & ((X1 == 0 & Y1 == 0 & X2 == 1 & Y2 == 1) | (X1 == 1 & Y1 == 1 & X2 == 2 & Y2 == 2) | (X1 == 0 & Y1 == 0 & X2 == 2 & Y2 == 2))) | 
    				  (mark(X1,Y1,S) & mark(X2,Y2,S) & X \== X1 & X \== X2 & Y \== Y1 & Y \== Y2 & ((X1 == 0 & Y1 == 2 & X2 == 1 & Y2 == 1) | (X1 == 1 & Y1 == 1 & X2 == 2 & Y2 == 0) | (X1 == 0 & Y1 == 2 & X2 == 2 & Y2 == 0))).


/* Blocking move: If the rival can complete a line, block it */
block(X, Y) :- rivalSymbol(R) & completesLine(X, Y, R).



started.

/* Define mySymbol and rivalSymbol */
+symbol(S) <- +mySymbol(S); .print("My symbol is: "); .print(S).
+rivalSymbol(R) <- mySymbol(S) & R \== S & R \== "_".



/* Plans */

/* When the agent is started, perform the 'sayHello' action. */
+started <- sayHello.


/* Check if we can win the game and play there */
+round(Z) : next & available(X,Y) & win(X,Y) <- play(X,Y);
			.print("Played Winning Move").

/* Check if opponent can win and block the move */
+round(Z) : next & available(X,Y) & block(X,Y) <- play(X,Y);
			.print("Played Blocking Move").

/* Play center if it is available */
+round(Z) : next & available(1,1) <- play(1,1);
			.print("Played Center").

/* Play corner if available */
+round(Z) : next & available(X,Y) & corner(X,Y) <- play(X,Y);
			.print("Played Corner").

/* Play an edge if there is not a better move */
+round(Z) : next & available(X,Y) <- play(X,Y);
			.print("Played BAD Move").

						 
						 
/* If I am the winner, then print "I won!"  */
+winner(S) : symbol(S) <- .print("I won!").

+end <- confirmEnd.
