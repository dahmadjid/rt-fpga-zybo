module rom #(
	parameter DATA_WIDTH = 32,
	parameter ADDR_WIDTH = 16,
	parameter INIT_DATA_FILE = "test.data"
) (
	input clk,
	input wire [ADDR_WIDTH-1:0] a,
	output reg [DATA_WIDTH-1:0] dout
);

	(* ram_style = "block" *) reg [DATA_WIDTH-1:0] ROM [2**ADDR_WIDTH-1:0];

	initial begin
		$readmemb(INIT_DATA_FILE, ROM);
	end

	always @(posedge clk) begin
		dout <= ROM[a];
	end
endmodule