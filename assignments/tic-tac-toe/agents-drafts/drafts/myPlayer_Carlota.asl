
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


started.


/* Plans */

/* When the agent is started, perform the 'sayHello' action.*/
+started <- sayHello.

/* Whenever it is my turn, play a random move. Specifically:
	- find all available cells and put them in a list called AvailableCells.
	- Get the length L of that list.
	- pick a random integer N between 0 and L.
	- pick the N-th cell of the list, and store its coordinates in the variables A and B.
	- mark that cell by performing the action play(A,B).
*/
+round(Z) : next <- .findall(available(X,Y),available(X,Y),AvailableCells);
						L = .length(AvailableCells);
						N = math.floor(math.random(L));
						.nth(N,AvailableCells,available(A,B));
						 play(A,B).


/* BETTER PERFORMANCE:
	- Check for a winning move before playing
	- Block the opponent from winning
	- Play in the center if available

*/

/* Adding a function to check if the agent can win */
threeInRow(X,Y,S) :- isCell(X,Y) & symbol(S) & mark(X,Y1,S) & mark(X,Y2,S) &
(Y1 \== Y & Y2 \== Y & Y1 \== Y2).

threeInColumn(X,Y,S) :- isCell(X,Y) & symbol(S) & mark(X1, Y, S) & mark(X2, Y, S) &
(X1 \== X & X2 \== X & X1 \== X2).

threeInDiagonal(X,Y,S) :- 
	(X == 0 & Y == 0) | (X == 1 & Y == 1) | (X == 2 & Y == 2) & 
	symbol(S) &
	mark(X1, Y1, S) & mark(X2, Y2, S) &
	(X1 \== X & X2 \== X & X1 \== X2) &
	(Y1 \== Y & Y2 \== Y & Y1 \== Y2).

threeInDiagonal(X,Y,S) :- 
    (X == 0 & Y == 2) | (X == 1 & Y == 1) | (X == 2 & Y == 0) &
    symbol(S) &
    mark(X1, Y1, S) & mark(X2, Y2, S) & 
    (X1 \== X & X2 \== X & X1 \== X2) & 
    (Y1 \== Y & Y2 \== Y & Y1 \== Y2).

winningMove(X,Y) :- symbol(S) & (threeInRow(X,Y,S) | threeInColumn(X,Y,S) | threeInDiagonal(X,Y,S)).
canWin(X,Y) :- available(X,Y) & winningMove(X,Y).


/* Adding a function to check if the agent can block the other player*/
canBlock(X,Y) :- available(X,Y) & opponentWinningMove(X,Y).

opponentWinningMove(X,Y) :- opponentSymbol(S) & 
    (threeInRow(X,Y,S) | threeInColumn(X,Y,S) | threeInDiagonal(X,Y,S)).

opponentSymbol(x) :- symbol(o).
opponentSymbol(o) :- symbol(x).

/* MAIN code */
// If I can win, then play the winning move.
+round(Z) : next & canWin(A,B) <- play(A,B).

// If I can't win but can block, then block the opponent.
+round(Z) : next & canBlock(A,B) <- play(A,B).

// If the center is free, play in the center.
+round(Z) : next & available(1,1) <- play(1,1).

// Otherwise, pick a random available move.
+round(Z) : next <- 
    .findall(available(X,Y), available(X,Y), AvailableCells);
    L = .length(AvailableCells);
    N = math.floor(math.random(L));
    .nth(N, AvailableCells, available(A,B));
    play(A,B).

		 
						 
/* If I am the winner, then print "I won!"  */
+winner(S) : symbol(S) <- .print("I won!").

+end <- confirmEnd.
