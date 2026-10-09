# M05 E1 part 1 of 4 -- complete read

refs.json sha256: 497d399005cefd631922aa62ce3298a98a0eb7b4863aae9000e2385502f67e7d

Read wave M05-E1-P1.ORACLE-COMPILER-REFERENCE-READ (plan v9b r1), base b3b686b3804d0d4bf533e066606c646542ccdc38, authority issue 1 checkpoint 6072776381 task 6051723926. This is a fresh read by a new isolated reader; the earlier read of this part (2c4cef2) was not consulted.

## Method

- Protocol: `python3 experiments/oracle_ingest/m05_check.py --protocol` output sha256 66e13172e565b21189008995b936a1b5a931dff205ae2f794bca04eb57835873, as planned.
- Hand-off: refs.json existed; `python3 experiments/oracle_ingest/c04_refs.py --verify` reported every embedded hash current (19 files), exit 0. Its sha256 equals the operator copy refs-497d3990.json.
- Rule total re-derived from refs.json: E1 has 529 RESOLVED rows; part 1 is rows [0, 132) in (class, row_id) order, 132 rows: E1:cast 47, E1:counter 32, E1:create 1, E1:destroy 49, E1:discard 3.
- Cards first: for every row the reader read paragraph_text and ref_text, decided which earlier action the phrase this way points to under CR 608.2c (the reference names the event of an earlier instruction in the same resolving text), and only then compared that with the endpoint region refs.json records. Every row was read; none was inferred from a neighbour.
- DUPLICATE: the span [char_offset, char_offset + len(phrase)) of each part row was compared with every other row of the M05 read set (all five rules plus fixtures, 1910 distinct rows) and with every refs.json candidate at the same clause address; no intersection exists.
- No rule, refs.json or c04_refs.py was edited (RULES FROZEN).

## Ledger

| row | class | endpoint | kind | duplicate | note |
|---|---|---|---|---|---|
| 00e8b4c9-3a79-4864-a730-c0081d397c5b:0:1:2@57:this way | E1:cast | yes | yes | yes | "cast that card without paying its mana cost" is the cast event that this way names, in clause 1; EVENT region, no overlapping span |
| 04e7f739-fe50-440d-aa3d-e547295044a8:0:1:1@20:this way | E1:cast | yes | yes | yes | "cast spells from among cards in your graveyard you've surveilled" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| 0b65dc8d-a8bf-4fa1-a44e-6a3782d18c0f:0:0:2@64:this way | E1:cast | yes | yes | yes | "cast an instant or sorcery spell with mana value X" is the cast event that this way names, in clause 1; EVENT region, no overlapping span |
| 0b95c115-6745-4ce1-896b-9021e93c161e:0:0:2@44:this way | E1:cast | yes | yes | yes | "cast that card without paying its mana cost" is the cast event that this way names, in clause 1; EVENT region, no overlapping span |
| 27065d34-b22a-47af-aea2-980f47bafcea:0:1:1@22:this way | E1:cast | yes | yes | yes | "cast this card from your graveyard by paying {U} rather" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| 2bd111bb-ce02-414c-b5b7-e0e037d8d96b:0:1:1@20:this way | E1:cast | yes | yes | yes | "cast spells from the top of your library" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| 2d44bdd2-aa31-415a-be71-d9e98ef12334:0:1:1@20:this way | E1:cast | yes | yes | yes | "cast artifact spells from your graveyard by paying 3 life" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| 2fa6f1b1-00af-433f-b8e1-36db99cd9bba:0:0:1@16:this way | E1:cast | yes | yes | yes | "cast instant and sorcery spells from the top of your" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| 30c0df75-9822-4016-a52b-d2e69dd58124:0:2:1@33:this way | E1:cast | yes | yes | yes | "cast Aura and Equipment spells from the top of your" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| 310c1280-dee8-426f-8440-6132a634a1e0:0:0:2@28:this way | E1:cast | yes | yes | yes | "cast that card without paying its mana cost if the" is the cast event that this way names, in clause 1; EVENT region, no overlapping span |
| 316e7c28-2b7a-40ae-961b-909644109fe4:0:0:2@29:this way | E1:cast | yes | yes | yes | "cast that card without paying its mana cost" is the cast event that this way names, in clause 1; EVENT region, no overlapping span |
| 3df11e5c-19aa-441c-a889-6b40eb3fdabf:0:1:2@20:this way | E1:cast | yes | yes | yes | "cast spells from among those cards this turn" is the cast event that this way names, in clause 1; EVENT region, no overlapping span |
| 3ef7e4c3-f87b-442d-8680-39673ede07e3:0:0:2@32:this way | E1:cast | yes | yes | yes | "cast that card without paying its mana cost" is the cast event that this way names, in clause 1; EVENT region, no overlapping span |
| 43e1b053-2cb9-4b1d-9e38-100cfa7267b6:0:0:3@26:this way | E1:cast | yes | yes | yes | "cast it without paying its mana cost" is the cast event that this way names, in clause 2; EVENT region, no overlapping span |
| 4b1da9aa-a30c-44b8-a10e-f9dc3fe70b6f:1:3:1@16:this way | E1:cast | yes | yes | yes | "cast instant and sorcery spells from any graveyard" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| 529178e8-425e-4d59-948c-ca7d0663f6ff:0:2:1@29:this way | E1:cast | yes | yes | yes | "cast Mutant, Ninja, or Turtle spells from the top of" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| 5b67a944-ab0b-4155-8bc0-becb1b38b3bb:0:0:2@44:this way | E1:cast | yes | yes | yes | "cast that card without paying its mana cost" is the cast event that this way names, in clause 1; EVENT region, no overlapping span |
| 5f1e9098-f554-4505-974b-cef4b4b7b23d:0:1:1@36:this way | E1:cast | yes | yes | yes | "cast target instant, sorcery, or artifact card from your graveyard" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| 657c5473-f153-4dd2-94a0-d477cbc2451d:0:0:2@20:this way | E1:cast | yes | yes | yes | "cast target instant or sorcery card with mana value less" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| 6c06e2d5-1473-4ce6-bcf6-10dfbbe5f801:0:0:2@30:this way | E1:cast | yes | yes | yes | "cast the exiled card without paying its mana cost if" is the cast event that this way names, in clause 1; EVENT region, no overlapping span |
| 74e3243b-6707-4769-8767-7cf2ef71009a:0:2:1@20:this way | E1:cast | yes | yes | yes | "cast creature spells with power or toughness 1 or less" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| 75348d55-99cd-4dab-97be-1f818c43a69d:0:0:1@20:this way | E1:cast | yes | yes | yes | "cast an artifact spell from your graveyard" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| 791cbb7c-7935-4902-b050-9ea9d030e9fa:0:1:1@20:this way | E1:cast | yes | yes | yes | "cast creature spells from your graveyard by foraging in addition" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| 88fb1dd1-60fb-4f51-ac4d-30b43156a474:0:0:3@37:this way | E1:cast | yes | yes | yes | "cast that card without paying its mana cost" is the cast event that this way names, in clause 2; EVENT region, no overlapping span |
| 8c56530b-098a-4afd-9022-76bfaa1f6a7c:0:1:1@15:this way | E1:cast | yes | yes | yes | "cast this card from your graveyard as long as you've" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| 8d087fe0-d554-4d7c-ba22-32db2cf71887:0:1:1@20:this way | E1:cast | yes | yes | yes | "cast creature spells with mana value 3 or less by" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| 8f5ef838-839a-4eb0-8d65-c8c8def0a233:0:1:2@16:this way | E1:cast | yes | yes | yes | "cast it this turn" is the cast event that this way names, in clause 1; EVENT region, no overlapping span |
| 9d5f712a-d46c-4d7e-8fea-45fdadb458df:0:2:1@35:this way | E1:cast | yes | yes | yes | "cast spells from among cards exiled with this enchantment" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| 9df60bb7-2dd4-4d22-b814-f52145356424:0:1:2@57:this way | E1:cast | yes | yes | yes | "cast that card without paying its mana cost" is the cast event that this way names, in clause 1; EVENT region, no overlapping span |
| a06fa827-900b-46d4-8f48-b4e15964951a:0:1:1@20:this way | E1:cast | yes | yes | yes | "cast spells from among cards exiled with this creature" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| a0a79e9e-38cb-45d8-a7ec-7cf10ef7e5fc:0:0:2@30:this way | E1:cast | yes | yes | yes | "cast up to two sorcery spells with mana value 3" is the cast event that this way names, in clause 1; EVENT region, no overlapping span |
| a0e85762-e433-4a23-bbee-69daeebb5898:0:1:2@32:this way | E1:cast | yes | yes | yes | "cast that card without paying its mana cost" is the cast event that this way names, in clause 1; EVENT region, no overlapping span |
| a1602bd0-f346-43cf-86ec-1dd300a7f2ed:0:2:1@29:this way | E1:cast | yes | yes | yes | "cast creature spells with power 4 or greater from the" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| a9d58cad-c1c2-4bd2-80f2-da9ce60801df:0:0:3@20:this way | E1:cast | yes | yes | yes | "cast spells from one of those piles" is the cast event that this way names, in clause 2; EVENT region, no overlapping span |
| b0c28b2b-a2dd-4b76-bb1c-cec55a0a6784:1:0:1@16:this way | E1:cast | yes | yes | yes | "cast a spell from each opponent's graveyard without paying its" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| bdef246c-cf66-40a1-aae4-a591846e73ca:0:0:2@21:this way | E1:cast | yes | yes | yes | "cast the exiled card without paying its mana cost if" is the cast event that this way names, in clause 1; EVENT region, no overlapping span |
| bedcb58e-7958-4364-8783-790ab52f92ea:0:4:1@20:this way | E1:cast | yes | yes | yes | "cast creature spells from your graveyard" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| cbbe535b-12d6-4e6c-8b26-9220f06a1604:0:1:2@53:this way | E1:cast | yes | yes | yes | "cast the exiled card without paying its mana cost if" is the cast event that this way names, in clause 1; EVENT region, no overlapping span |
| cca15007-2faf-4696-a4c5-2d7b6c1ec5b5:0:0:1@36:this way | E1:cast | yes | yes | yes | "cast up to one target card of the other type" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| d1438681-241b-4d53-9470-4d04a7797ea8:0:0:1@16:this way | E1:cast | yes | yes | yes | "cast an instant or sorcery spell from your graveyard by" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| d6026309-aae9-43e7-938b-69db7af7139c:0:2:1@20:this way | E1:cast | yes | yes | yes | "cast Dinosaur creature spells from among cards you own exiled" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| d6fafb50-9531-4fbf-bb1e-ebb4dd39281c:0:0:1@16:this way | E1:cast | yes | yes | yes | "cast up to one target instant card and/or up to" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| da339200-ed26-42e4-b24f-b96bc4daef7c:0:2:1@20:this way | E1:cast | yes | yes | yes | "cast noncreature spells from the top of your library" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| e537bd23-7368-459b-badf-b7b7c112c88a:0:1:2@20:this way | E1:cast | yes | yes | yes | "cast spells from among the exiled cards for as long" is the cast event that this way names, in clause 1; EVENT region, no overlapping span |
| f21ce158-2925-4658-ab7b-b73718d31965:0:1:1@16:this way | E1:cast | yes | yes | yes | "cast up to one target instant or sorcery card from" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| f5092c14-eec4-472c-999c-ba96c36b2fbb:0:1:1@16:this way | E1:cast | yes | yes | yes | "cast an instant or sorcery spell from your graveyard" is the cast event that this way names, in clause 0; EVENT region, no overlapping span |
| fe5690d3-547b-4ce9-8e94-77fdc0e9c5c6:0:1:2@43:this way | E1:cast | yes | yes | yes | "cast any number of spells from among cards exiled this" is the cast event that this way names, in clause 1; EVENT region, no overlapping span |
| 0146de73-29bf-415a-b450-11074553f715:0:0:1@27:this way | E1:counter | yes | yes | yes | "Counter target creature or enchantment spell" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| 085bc7be-bd44-40af-8e8f-a1a8006fe22c:0:1:1@27:this way | E1:counter | yes | yes | yes | "Counter target spell" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| 0c2abd2a-ca98-45d2-8dd1-984d2c0c266a:0:1:1@38:this way | E1:counter | yes | yes | yes | "Counter target activated or triggered ability" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| 0ec5a688-a884-410c-adee-ab784789d6e8:0:1:1@38:this way | E1:counter | yes | yes | yes | "counter target activated or triggered ability from an artifact or" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| 11ed8209-2184-4416-a8f0-72de00599574:0:1:1@99:this way | E1:counter | yes | yes | yes | "Counter all spells your opponents control and all abilities your" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| 198fed4c-297e-41c0-a172-e471c7401fbb:0:0:1@27:this way | E1:counter | yes | yes | yes | "Counter target creature or planeswalker spell unless its controller pays" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| 1b721ad3-d0f6-4eec-9bf0-f57ea9dfa392:0:0:1@27:this way | E1:counter | yes | yes | yes | "Counter target spell" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| 2993dc7d-723d-4a9b-94bd-4bb02a9f7243:0:1:1@69:this way | E1:counter | yes | yes | yes | "counter up to one target activated or triggered ability" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| 318f7f70-e374-40ef-8afb-3389c10461d8:0:0:1@27:this way | E1:counter | yes | yes | yes | "Counter target spell unless its controller pays {X}" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| 3d9f854e-1ee5-4aa1-a33b-d3ae08f15dd0:0:1:1@27:this way | E1:counter | yes | yes | yes | "Counter target spell" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| 4b2e9aa9-6f91-41de-84b6-e9a89be06a53:0:0:1@27:this way | E1:counter | yes | yes | yes | "Counter target spell" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| 7687b2a7-816d-4416-979b-675e35e235fc:0:0:1@27:this way | E1:counter | yes | yes | yes | "Counter target spell" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| 7c6e0198-edd8-42b8-ba1b-549e1713d188:0:0:1@27:this way | E1:counter | yes | yes | yes | "Counter target creature or planeswalker spell" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| 983caa3f-7089-4e66-825d-4086a5adb9bb:0:0:1@26:this way | E1:counter | yes | yes | yes | "Counter target spell" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| 9cac23a1-a0b3-490c-aea2-dc2928f6dc9e:0:1:1@27:this way | E1:counter | yes | yes | yes | "Counter target creature spell with mana value 4 or less" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| ac2173f9-f223-440a-9231-fd98762bdc6f:0:1:1@27:this way | E1:counter | yes | yes | yes | "Counter target noncreature spell" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| b2faa8b6-e433-4171-9774-9170484530c4:0:0:1@38:this way | E1:counter | yes | yes | yes | "Counter target spell or ability an opponent controls that targets" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| b665a64b-4772-42dd-9fd2-fd8598e689ba:0:0:1@27:this way | E1:counter | yes | yes | yes | "Counter target creature spell" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| bbe370ba-412b-4052-89d9-2d0ae4928118:0:0:1@27:this way | E1:counter | yes | yes | yes | "Counter target non-Faerie spell" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| bbfb3e4a-b389-4391-8141-13b68c0ef2e0:0:0:1@27:this way | E1:counter | yes | yes | yes | "Counter target spell" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| bc2f807b-555d-4a62-ab14-75fe62c64b97:0:0:1@27:this way | E1:counter | yes | yes | yes | "Counter target spell" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| bfaf376f-90f9-45d9-bfbe-dd84a2a4688b:0:1:1@27:this way | E1:counter | yes | yes | yes | "Counter target spell unless its controller pays {4}" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| c01411e0-77b2-4e65-a369-5dbe13745769:0:1:1@27:this way | E1:counter | yes | yes | yes | "counter target spell" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| c9db6b94-a7b1-4b93-b454-4dead8f85e34:0:0:1@27:this way | E1:counter | yes | yes | yes | "Counter target spell" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| d4ab7848-5c37-4c6b-be29-0bb703333e5b:0:0:1@27:this way | E1:counter | yes | yes | yes | "Counter target spell" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| d71cd08e-3e84-41ff-b9db-9e343c0af6b4:0:0:1@27:this way | E1:counter | yes | yes | yes | "Counter target spell" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| dc9ae094-139f-4f28-9d4e-4d6def765744:0:0:1@27:this way | E1:counter | yes | yes | yes | "Counter target spell with mana value 3 or less" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| e83a629e-2d74-48e2-ad4d-f390067cc51a:0:2:1@27:this way | E1:counter | yes | yes | yes | "counter target spell" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| ead1ee6a-e0da-46d5-89e8-31e8c0270bc2:0:0:1@27:this way | E1:counter | yes | yes | yes | "Counter target spell unless its controller pays {3}" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| ec45caf7-2051-463d-bf70-3dda671d6ce2:0:0:1@37:this way | E1:counter | yes | yes | yes | "Counter all other spells" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| ee3d1f44-e0ca-4ce9-be76-4b675a115156:0:0:1@46:this way | E1:counter | yes | yes | yes | "Counter target spell" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| feb221fb-59bf-4671-a53f-1bbe8e9c2ca9:0:0:1@27:this way | E1:counter | yes | yes | yes | "Counter target spell" is the counter event that this way names, in clause 0; EVENT region, no overlapping span |
| 8a3ad2ef-8bcb-40c0-85de-f03328c2b644:0:2:2@29:this way | E1:create | yes | yes | yes | "create a token that's a copy of that creature" is the create event that this way names, in clause 1; EVENT region, no overlapping span |
| 011d4f47-c6fd-434b-98f2-2f558fbff40b:0:0:1@45:this way | E1:destroy | yes | yes | yes | "Destroy all artifacts and enchantments" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| 14062abe-14df-4dbe-ad7b-530e5f6c4988:0:0:1@24:this way | E1:destroy | yes | yes | yes | "Destroy all Plains" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| 15e5136e-ed15-49a8-b027-e09436673fb4:0:0:1@44:this way | E1:destroy | yes | yes | yes | "Destroy each nonland permanent with mana value 2 or less" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| 21c77cdb-9ba1-4621-b096-7eb94c076cef:0:0:1@47:this way | E1:destroy | yes | yes | yes | "Destroy up to X target artifacts" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| 2f109125-b743-4ecf-84da-690d8e8ddf9c:0:0:1@115:this way | E1:destroy | yes | yes | yes | "Destroy all creatures" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| 3d3fd8a2-78d4-4f52-8fcd-0c6fa93f0043:0:1:2@20:this way | E1:destroy | yes | yes | yes | "destroy each artifact with mana value less than or equal" is the destroy event that this way names, in clause 1; EVENT region, no overlapping span |
| 3e229329-65e4-4240-959a-b97b26908c0e:0:0:1@24:this way | E1:destroy | yes | yes | yes | "Destroy all nonbasic lands" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| 4d00c44b-8953-4b18-af73-2944321b6cd1:0:0:1@21:this way | E1:destroy | yes | yes | yes | "Destroy target creature if it shares a color with the" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| 51f9a6cc-8eb2-44ed-a2d9-913ac514ad67:0:0:1@66:this way | E1:destroy | yes | yes | yes | "destroy all artifacts and enchantments" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| 52b88034-bf0f-4d29-b776-40ce421f1107:0:1:1@29:this way | E1:destroy | yes | yes | yes | "destroy target noncreature permanent that player controls" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| 53d5d961-d6a3-49b1-b335-2c2b49972008:0:1:1@65:this way | E1:destroy | yes | yes | yes | "destroy all creatures with flying" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| 53e86135-3b24-4618-bcc0-af4d81e672dd:0:0:1@41:this way | E1:destroy | yes | yes | yes | "Destroy all creatures and enchantments" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| 55281479-9d30-4f3e-afd0-66b0df5de68c:0:0:1@24:this way | E1:destroy | yes | yes | yes | "Destroy target artifact, enchantment, or land" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| 5dc34e93-97e3-434b-9f12-f45c6d556f13:0:0:1@29:this way | E1:destroy | yes | yes | yes | "Destroy all artifacts and enchantments" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| 65a64759-3a93-4542-84fc-3af5ccb741f4:0:1:1@44:this way | E1:destroy | yes | yes | yes | "Destroy all creatures" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| 6ef3c75d-6af2-4ea0-b98d-96c5d7d3af58:0:0:0@139:this way | E1:destroy | yes | yes | yes | "Destroy all creatures" is the destroy event that this way names, earlier in the same clause; EVENT region, no overlapping span |
| 75f5d372-4ff9-430c-8302-72472439e0d2:0:0:1@37:this way | E1:destroy | yes | yes | yes | "Destroy all creatures" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| 79a63064-f25b-4c34-867e-a9d32da97b14:0:1:1@24:this way | E1:destroy | yes | yes | yes | "destroy up to one nonbasic land that player controls" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| 80d233cc-7748-41a2-bfd6-2189d0136900:0:0:1@21:this way | E1:destroy | yes | yes | yes | "Destroy target creature if it's white" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| 88075828-a76e-412d-b738-182f50e3a133:0:1:1@43:this way | E1:destroy | yes | yes | yes | "destroy up to one target creature that player controls" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| 8b59cacb-46ff-4400-a7f6-b258c81a9b14:0:1:2@21:this way | E1:destroy | yes | yes | yes | "destroy that creature unless its controller pays 2 life" is the destroy event that this way names, in clause 1; EVENT region, no overlapping span |
| 932668fa-d6e3-41c0-ad0c-8e0a00e68d11:0:0:2@40:this way | E1:destroy | yes | yes | yes | "Destroy all creatures" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| 998daf11-c0ed-4801-b013-d8b3136f16d1:0:0:1@28:this way | E1:destroy | yes | yes | yes | "destroy up to one target artifact" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| 9fb7e7ca-ad2f-4677-859c-7a9adf8fb5fd:0:1:1@31:this way | E1:destroy | yes | yes | yes | "Destroy target artifact or creature you don't control" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| a07b3aa8-9240-4ec6-918e-7e1ae719904c:0:0:1@56:this way | E1:destroy | yes | yes | yes | "Destroy up to three target artifacts" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| a648b9ed-810a-41db-af40-3b5b4658db90:0:0:2@20:this way | E1:destroy | yes | yes | yes | "destroy all creatures" is the destroy event that this way names, in clause 1; EVENT region, no overlapping span |
| a77b5be2-f361-4135-ba25-670a74d268ac:0:1:1@27:this way | E1:destroy | yes | yes | yes | "destroy another target creature" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| b01d61cc-9844-4191-86a0-f2db6d42d6e5:0:0:1@21:this way | E1:destroy | yes | yes | yes | "Destroy target creature" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| b17ea905-0696-4e58-b564-557e87236e27:0:0:1@44:this way | E1:destroy | yes | yes | yes | "Destroy all creatures" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| b233473d-d22b-45e4-9fe7-55d1170a788b:0:0:1@47:this way | E1:destroy | yes | yes | yes | "Destroy all enchantments" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| b4faba1a-23db-4678-9ce6-a7816105f22a:0:1:1@70:this way | E1:destroy | yes | yes | yes | "destroy the other creature at end of combat" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| b5516bc9-ec8d-4323-8748-96c49d7d0622:0:0:1@92:this way | E1:destroy | yes | yes | yes | "Destroy all creatures" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| b9d51e07-851f-4b7b-bffe-7c1efff0714c:0:0:1@55:this way | E1:destroy | yes | yes | yes | "Destroy target enchantment" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| bc8de6c7-c69d-4add-8f25-825d945874f9:0:0:1@82:this way | E1:destroy | yes | yes | yes | "Destroy all creatures" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| bca7101b-e74b-42af-ac63-1b3defb4137d:0:0:2@28:this way | E1:destroy | yes | yes | yes | "Destroy all creatures" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| bdccceb6-ad3c-4a75-a8a6-ca796ede4185:0:0:1@40:this way | E1:destroy | yes | yes | yes | "Destroy all creatures target opponent controls" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| cb19d2f7-0511-4c66-ba4c-f38516920c20:0:0:1@28:this way | E1:destroy | yes | yes | yes | "Destroy target artifact or land" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| d32c6f64-c4b0-4451-8986-a0abc1fc2bb3:0:0:1@28:this way | E1:destroy | yes | yes | yes | "Destroy any number of target creatures" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| d73df13d-942a-4104-ac9d-de7c100c086f:0:1:1@30:this way | E1:destroy | yes | yes | yes | "destroy this creature unless you pay {3}{B}{B}{B}" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| d92714c0-4e22-47f9-a4d4-405894e734d0:0:1:1@32:this way | E1:destroy | yes | yes | yes | "Destroy target creature or enchantment" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| e14ac0f3-00d5-4a95-990c-b7ea157bb87e:0:0:1@47:this way | E1:destroy | yes | yes | yes | "Destroy all enchantments" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| e2048201-6dc9-4cf5-916f-1d867ae8dbdd:0:0:1@44:this way | E1:destroy | yes | yes | yes | "Destroy all creatures target opponent controls" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| e2161ae2-e5d2-4a56-85d4-d2214c5b3e2e:0:0:1@29:this way | E1:destroy | yes | yes | yes | "Destroy X target artifacts and/or creatures" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| ea38a211-a7b0-49fe-b5dc-7eca7610cccb:0:0:1@21:this way | E1:destroy | yes | yes | yes | "Destroy target creature unless its controller pays life equal to" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| ed68160e-5e3d-44f2-ac7a-3749fda10119:0:0:1@20:this way | E1:destroy | yes | yes | yes | "Destroy all lands or all creatures" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| ef7fce1b-0d95-4f92-a8ad-09d9756fa0e4:0:1:1@28:this way | E1:destroy | yes | yes | yes | "destroy up to one target creature that player controls" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| eff0a1ad-ecc6-416f-a4ae-96b26cd8a905:0:0:2@63:this way | E1:destroy | yes | yes | yes | "Destroy any number of target planeswalkers" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| f0ff2c1c-702d-406b-a426-4282117afe8e:0:0:1@44:this way | E1:destroy | yes | yes | yes | "Destroy all tapped creatures" is the destroy event that this way names, in clause 0; EVENT region, no overlapping span |
| fd57331f-1cfa-4f88-a925-fc171738c3c0:0:0:2@21:this way | E1:destroy | yes | yes | yes | "destroy that creature" is the destroy event that this way names, in clause 1; EVENT region, no overlapping span |
| 01766d9b-b2af-4a27-9e65-08c82e7d7637:0:0:1@24:this way | E1:discard | yes | yes | yes | "Discard your hand" is the discard event that this way names, in clause 0; EVENT region, no overlapping span |
| 02238355-9c84-4ae0-b850-269f460144a8:0:0:1@32:this way | E1:discard | yes | yes | yes | "discard two cards" is the discard event that this way names, in clause 0; EVENT region, no overlapping span |
| 10c2428f-6e4a-4b92-9087-720242a5c25c:0:0:1@76:this way | E1:discard | yes | yes | yes | "Discard all the cards in your hand" is the discard event that this way names, in clause 0; EVENT region, no overlapping span |

## Observations

- Every endpoint is the region of the frozen head verb that the participle before this way governs: the cast permission for cast rows (for play-lands-and-cast permissions the region is the cast half, which is what a spell cast this way means), the counter instruction for counter rows, the token creation for the create row, the destroy instruction for destroy rows and the discard instruction for discard rows.
- Rows whose endpoint is two or more clauses back were checked against the whole paragraph: the intervening clause (a they-can't-be-regenerated sentence, a replacement sentence, a choice, a guess) carries no competing instruction of the same verb. Where the paragraph opens with a cast trigger (Whenever you cast ...), the endpoint is the later cast permission, which is what the reference means.
- Row 6ef3c75d-6af2-4ea0-b98d-96c5d7d3af58:0:0:0@139:this way resolves inside its own clause to a region starting before the offset; that region is the destroy instruction the count refers to.
- Kind EVENT is right for every row: this way names an action taken, not an object.

## Verdict

- E1/P1: PASS (rows 132, endpoint-no 0, kind-no 0, duplicate-no 0, cannot-judge 0); every endpoint is the event its this way names.

## Captain questions

None.
