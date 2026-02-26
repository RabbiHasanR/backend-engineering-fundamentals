PL/pgSQL is a block structured language. Heres the systax of a block in PL/pgSQL:

[ <<label>> ]
[ declare
    declarations ]
begin
    statements;
    ...
end [ label ];

each block has two sections:
    Declarations
    Body