module ram #(
	parameter DATA_WIDTH = 32,
	parameter ADDR_WIDTH = 16,
	parameter INIT_DATA_FILE = "test.data"
) (
	input clk,
	input we,
	input wire [ADDR_WIDTH-1:0] a,
	input wire [DATA_WIDTH-1:0] di,
	output reg [DATA_WIDTH-1:0] dout
);

	(* ram_style = "block" *) reg [DATA_WIDTH-1:0] RAM [0:2**ADDR_WIDTH-1];

	initial begin
		$readmemb(INIT_DATA_FILE, RAM);
	end

	always @(posedge clk) begin
		if (we) begin
			RAM[a] <= di;
			dout <= di;
		end else
			dout <= RAM[a];
	end
endmodule