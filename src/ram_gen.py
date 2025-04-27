ram_template = """
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity ram is
generic (
	DATA_WIDTH: natural := 32;
	ADDR_WIDTH: natural := 16;
);
port(
	clk : in std_logic;
	we : in std_logic;
	a : in std_logic_vector(ADDR_WIDTH-1 downto 0);
	di : in std_logic_vector(DATA_WIDTH-1 downto 0);
	do : out std_logic_vector(DATA_WIDTH-1 downto 0)
);
end ram;

architecture arch of ram is
	type ram_type is array (0 to 2**ADDR_WIDTH-1) of std_logic_vector(DATA_WIDTH-1 downto 0);
	signal RAM : ram_type := __DEFAULT_RAM_VALUE__;
    attribute ram_style : string;
    attribute ram_style of RAM : signal is "block";
begin
	process(clk)
	begin
		if (clk'event and clk = '1') then
			if (we = '1') then
				RAM(to_integer(unsigned(a))) <= di;
			end if;
            do <= RAM(to_integer(unsigned(a)));
		end if;
	end process;


end architecture;
"""