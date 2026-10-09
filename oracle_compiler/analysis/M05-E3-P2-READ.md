# M05 E3 part 2 of 2 -- complete read

refs.json sha256: 497d399005cefd631922aa62ce3298a98a0eb7b4863aae9000e2385502f67e7d

Read wave M05-E3-P2.ORACLE-COMPILER-REFERENCE-READ (plan v9b r1), base 9ea397f3084ada1a24ba377cb65023778a6e91ce, authority issue 1 checkpoint 6076695359 task 6051725022. This is a fresh read by a new isolated reader. The E2 part 4 document was consulted only for document layout. No other read document, and no earlier reader's scratch output, was consulted for any row verdict.

## Method

- Protocol: `python3 experiments/oracle_ingest/m05_check.py --protocol` output sha256 66e13172e565b21189008995b936a1b5a931dff205ae2f794bca04eb57835873, as planned. INTERFACES.md at the base is blob 282c295c03f2a4b43e723d01710baaf479aa716c. For each of the five RULES FROZEN files, `git rev-parse HEAD:[file]` equals the blob at the C04 accepted head b3b686b3804d0d4bf533e066606c646542ccdc38.
- Hand-off: refs.json existed. `python3 experiments/oracle_ingest/c04_refs.py --verify` reported every embedded hash current (19 files), exit 0. Its sha256 equals the operator copy refs-497d3990.json.
- Rule total re-derived from refs.json: E3 has 196 RESOLVED rows (and 12 UNRESOLVED, not read), matching the I5.4 figure. In (class, row_id) order, part 2 is rows [98, 196): 98 rows, all class E3, all endpoint kind PRODUCT, all phrase "the copy". The ledger order equals `--skeleton --rule E3 --part 2`.
- Cards first: for every row the reader read paragraph_text and ref_text (face_text where the paragraph alone was not enough) and decided, under the Comprehensive Rules, which printed copy instruction creates the copy the reference names. Only then was that compared with the endpoint clause and its endpoint_text. Every row was read; none was inferred from a neighbour.
- CR read through experiments/foundry_cr.py: 707.10 (to copy a spell or ability puts a copy of it onto the stack), 707.10c (an effect copies and its controller may choose new targets for the copy), 707.10e (an effect copies and specifies a new target for the copy), 707.10f (a copied permanent spell), 707.12 (an instruction to cast a copy of an object), 707.9 (copy effects with modifications or exceptions). In each case the copy is the object the copy instruction creates.
- Endpoint position: 87 endpoints are an earlier clause of the reference paragraph; 11 are earlier in the reference clause itself ("copy that spell and you may choose new targets for the copy", "copy it, except the copy isn't legendary"). 18 rows are flagged delayed in refs.json: the copy instruction sits in a delayed or reflexive trigger in the same paragraph, follows that trigger's condition after its closing comma, and the reference is in the same trigger. Reference shapes: new targets for the copy 74 (707.10c), cast the copy 17 (707.12), the copy targets a specified object 3 (707.10e), the copy as a permanent spell 2 (707.10f), an exception to the copy 2 (707.9).
- Checked cases: where one instruction makes several copies ("for each of those creatures, copy that spell"; "Each opponent may copy that spell"), "the copy" names each copy made by that instruction, so the endpoint is still that instruction. Where the copied object is a card ("copy the exiled card", "copy the other", "copy a card exiled with ~"), the reference is the card copy that is then cast (707.12).
- KIND: PRODUCT for every row, which is right: in every row the referenced copy is the object the endpoint instruction creates (measurement labels only, I5.8 ruling 5).
- DUPLICATE: the span [char_offset, char_offset + len(phrase)) of each part row was compared with every row of the M05 read set (all five rules' read rows plus the fixtures, 1910 rows) at the same clause address, and with every other refs.json candidate. No part row intersects another row.
- Each note quotes, from endpoint_text, the copy instruction the reference points to (at most 7 words, verbatim), its position, and the CR rule it was read under.
- No rule, refs.json or c04_refs.py was edited (RULES FROZEN).

## Ledger

| row | class | endpoint | kind | duplicate | note |
|---|---|---|---|---|---|
| 78ac1e6c-2704-4844-9e87-642324c23997:0:0:2@13:the copy | E3 | yes | yes | yes | "Copy it" (clause 1, earlier in the paragraph) creates the copy of the card that is then cast, CR 707.12; PRODUCT |
| 792f8235-f23b-4858-bdd4-c7a186b7a470:0:1:2@13:the copy | E3 | yes | yes | yes | "Copy that card" (clause 1, earlier in the paragraph) creates the copy of the card that is then cast, CR 707.12; PRODUCT |
| 7db22241-fe43-4071-9af9-de1cf394f7f5:1:1:1@31:the copy | E3 | yes | yes | yes | "Copy target instant or sorcery spell" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| 7ef7d902-1f05-40b3-8997-dec197b0b678:0:1:1@42:the copy | E3 | yes | yes | yes | "copy it" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| 7ef7d902-1f05-40b3-8997-dec197b0b678:0:1:2@3:the copy | E3 | yes | yes | yes | "copy it" (clause 0, earlier in the paragraph) creates the copy of the spell the condition tests, CR 707.10f; PRODUCT |
| 8088d110-2314-45c3-b6ee-3f55d1f388e4:0:3:1@31:the copy | E3 | yes | yes | yes | "Copy target instant or sorcery spell" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| 82922f3a-a444-49cf-b136-f30a3c85f791:0:0:2@73:the copy | E3 | yes | yes | yes | "copy that spell and you may choose" (earlier in the same clause) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| 8514f20a-50c7-4319-84cb-2bf263548234:0:1:3@31:the copy | E3 | yes | yes | yes | "copy that spell" (clause 2, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| 85845b6c-abb5-4591-b987-a375972cf25b:0:1:1@31:the copy | E3 | yes | yes | yes | "copy that spell" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| 869c9bc4-2b21-40c3-8b1c-c83269c856d0:0:1:1@31:the copy | E3 | yes | yes | yes | "copy that spell" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| 8c35fd11-be45-4984-bd83-6e4f3fbc47a9:0:0:2@31:the copy | E3 | yes | yes | yes | "copy that spell" (clause 1, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| 8d0da2f9-0e05-4a94-8d42-fd57d06b09ba:0:1:1@31:the copy | E3 | yes | yes | yes | "Copy target instant or sorcery spell you" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| 8d35cef8-a52d-45fb-8f5f-cccea26826d0:0:2:2@31:the copy | E3 | yes | yes | yes | "copy it" (clause 1, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| 8e4d0da0-c7d8-4a20-9bfd-02c1331a7a49:1:1:1@112:the copy | E3 | yes | yes | yes | "copy that spell and you may choose" (earlier in the same clause) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| 8ea414c1-88cf-46d4-9a54-6dee9847c537:0:0:3@13:the copy | E3 | yes | yes | yes | "copy the exiled card" (clause 2, earlier in the paragraph) creates the copy of the card that is then cast, CR 707.12; PRODUCT |
| 8eb7c0a5-6190-40de-b473-2d1daa3bbe28:0:1:1@31:the copy | E3 | yes | yes | yes | "copy target instant or sorcery spell" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| 8f6a2fce-719e-4745-80d3-aabce5c9bafa:0:0:2@31:the copy | E3 | yes | yes | yes | "copy that spell" (clause 1, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| 8f878efc-850f-43d2-a6fe-5ea8d1dd5afb:0:0:1@31:the copy | E3 | yes | yes | yes | "Copy target instant or sorcery spell" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| 938ba053-35f6-4424-a978-bf915709572c:0:0:2@24:the copy | E3 | yes | yes | yes | "copy an instant or sorcery card in" (clause 1, earlier in the paragraph) creates the copy of the card that is then cast, CR 707.12; PRODUCT |
| 93989dd7-2d3e-46e2-8e92-8d0479796087:0:1:1@31:the copy | E3 | yes | yes | yes | "copy that spell" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| 93da1e63-54d6-4b05-af91-f13e7e111176:0:1:1@31:the copy | E3 | yes | yes | yes | "Copy target instant or sorcery spell" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| 946675f5-8998-4f1b-934b-85ffe6e2f002:0:0:1@31:the copy | E3 | yes | yes | yes | "copy that spell" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| 957413ae-e756-4afe-886a-b57bf59d5f8d:0:1:2@0:the copy | E3 | yes | yes | yes | "copy that spell" (clause 1, earlier in the paragraph) creates the copy whose new target the effect specifies, CR 707.10e; PRODUCT |
| 96cc63af-69d1-4493-b241-0cb244a9e48a:0:1:2@31:the copy | E3 | yes | yes | yes | "copy that ability" (clause 1, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| 9794e31f-e73d-4aa0-a421-dc496080c987:1:0:1@31:the copy | E3 | yes | yes | yes | "copy that spell" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| 97a85a3e-258e-49b7-8ebe-7efee808da7a:0:1:1@31:the copy | E3 | yes | yes | yes | "copy it" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| 97a85a3e-258e-49b7-8ebe-7efee808da7a:0:1:2@27:the copy | E3 | yes | yes | yes | "copy it" (clause 0, earlier in the paragraph) creates the copy of the spell the condition tests, CR 707.10f; PRODUCT |
| 9aa6d116-b7a0-4f3a-90fc-5bbee8c0c3da:0:1:1@13:the copy | E3 | yes | yes | yes | "copy a card exiled with ~" (clause 0, earlier in the paragraph) creates the copy of the card that is then cast, CR 707.12; PRODUCT |
| 9aa8eef1-fc67-4d54-9783-4d0175a76741:0:1:1@24:the copy | E3 | yes | yes | yes | "copy the other" (clause 0, earlier in the paragraph) creates the copy of the card that is then cast, CR 707.12; PRODUCT |
| 9adc3750-0ddb-4f2c-a0e7-131e59d4cba5:0:1:1@31:the copy | E3 | yes | yes | yes | "copy that spell" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| 9c78778a-6335-4949-8ade-11d0f085cb2b:0:0:1@31:the copy | E3 | yes | yes | yes | "copy that spell" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| a1f55890-31c5-4ed4-a2cd-7a4a9f05f8ca:0:0:1@31:the copy | E3 | yes | yes | yes | "Copy target instant or sorcery spell" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| a45bb088-16fd-4d91-8fd6-3c52f1c24748:0:0:1@32:the copy | E3 | yes | yes | yes | "copy this spell" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| a498ca5f-7743-47b7-a57a-471efa1a99e8:0:0:1@31:the copy | E3 | yes | yes | yes | "copy that spell" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| a6657fcf-f08c-4b03-8ec8-cb0b194eb553:0:1:0@150:the copy | E3 | yes | yes | yes | "copy it and you may choose new" (earlier in the same clause) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| a968524a-3d2d-4c0c-8f66-bfbfb9ff3c36:0:2:1@31:the copy | E3 | yes | yes | yes | "copy that ability" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| ae9f5c80-bc96-4ab3-bb5b-e8bd470e9eab:0:1:2@31:the copy | E3 | yes | yes | yes | "copy that spell or ability" (clause 1, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| af566158-23b2-4f91-8d59-a58342a9f576:0:0:1@31:the copy | E3 | yes | yes | yes | "Copy target activated or triggered ability you" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| af6f771f-5154-4fb3-8ed4-768d71eea568:0:0:1@31:the copy | E3 | yes | yes | yes | "Copy target instant or sorcery spell with" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| b3a80545-9a8a-46b2-9d8c-b0d66fb68a5d:0:1:2@31:the copy | E3 | yes | yes | yes | "copy that spell" (clause 1, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| b446b485-c10b-4175-bb49-16ac2f9e7718:0:0:3@13:the copy | E3 | yes | yes | yes | "Copy that card" (clause 2, earlier in the paragraph) creates the copy of the card that is then cast, CR 707.12; PRODUCT |
| b6b22bac-853a-45a8-a74d-9904ec2b34fd:0:2:1@31:the copy | E3 | yes | yes | yes | "copy it" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| b7da26c9-78a6-41c5-a5ef-6555e8274d7a:0:2:1@31:the copy | E3 | yes | yes | yes | "copy that spell" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| b8501a37-23e4-4873-80cb-d1c0f6c95155:0:0:1@31:the copy | E3 | yes | yes | yes | "copy that spell" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| bbf9494c-c4bb-4d36-98fe-8387846b342e:0:0:2@31:the copy | E3 | yes | yes | yes | "copy that ability" (clause 1, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| bd56225e-8c80-4328-9ca0-0fff4969573d:0:1:2@31:the copy | E3 | yes | yes | yes | "copy that ability" (clause 1, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| c008d60a-ee06-4411-b8e7-c2df13616105:1:0:1@31:the copy | E3 | yes | yes | yes | "copy that spell" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| c098c507-5154-423a-a70b-f6dfd4959cf6:0:2:2@31:the copy | E3 | yes | yes | yes | "copy that spell or ability" (clause 1, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| c09c424b-6aba-4190-9f55-f0307d746386:0:0:1@31:the copy | E3 | yes | yes | yes | "Copy target activated or triggered ability you" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| c0d2bdd9-1e68-4d3a-83f8-ec2ba440a494:1:1:1@31:the copy | E3 | yes | yes | yes | "copy it" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| c2d04138-cc17-4dd0-9a4c-9c87df72ed01:0:1:3@13:the copy | E3 | yes | yes | yes | "Copy the exiled card" (clause 2, earlier in the paragraph) creates the copy of the card that is then cast, CR 707.12; PRODUCT |
| c33e99c6-189e-4dcf-8b6a-64937dbad361:0:2:1@31:the copy | E3 | yes | yes | yes | "copy it" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| c51ed6e3-813b-49c4-b1de-7f92a77f8f6e:0:0:1@31:the copy | E3 | yes | yes | yes | "copy that spell" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| c6a67820-5066-462f-a621-1ecab8bf4f97:0:1:1@31:the copy | E3 | yes | yes | yes | "copy the next loyalty ability you activate" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| c8fac933-b378-47e0-8f99-8b09b55b6403:0:2:1@31:the copy | E3 | yes | yes | yes | "copy that spell" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| cbd483b5-5554-43ed-a729-535d01b0d5d3:0:3:1@31:the copy | E3 | yes | yes | yes | "copy it" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| cbf64c58-664f-431f-987e-08ae70d23f2b:0:0:1@65:the copy | E3 | yes | yes | yes | "copy that spell and may choose new" (earlier in the same clause) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| cc18e782-a965-404f-96f1-348f3ed799fd:0:1:2@13:the copy | E3 | yes | yes | yes | "Copy it" (clause 1, earlier in the paragraph) creates the copy of the card that is then cast, CR 707.12; PRODUCT |
| cf5f4860-e805-46a3-9352-a2c583e33403:0:1:0@63:the copy | E3 | yes | yes | yes | "copy it, except the copy isn't legendary" (earlier in the same clause) creates the copy that the exception modifies, CR 707.9; PRODUCT |
| cf5f4860-e805-46a3-9352-a2c583e33403:0:1:1@31:the copy | E3 | yes | yes | yes | "copy it, except the copy isn't legendary" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| cf751552-156f-4f81-ac94-9814dce099f9:0:0:1@31:the copy | E3 | yes | yes | yes | "Copy target triggered ability you control" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| d04356f1-0e1a-4689-8e54-f88c4c6dd936:0:1:1@31:the copy | E3 | yes | yes | yes | "Copy target instant or sorcery spell you" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| d0e80414-abde-4f5e-9539-3efc83aa507f:0:1:2@13:the copy | E3 | yes | yes | yes | "Copy it" (clause 1, earlier in the paragraph) creates the copy of the card that is then cast, CR 707.12; PRODUCT |
| d1ce7fcf-42f8-4b35-9ba1-55033c65c43e:0:0:1@68:the copy | E3 | yes | yes | yes | "copy this spell and may choose new" (earlier in the same clause) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| d3bdd3f2-9e38-436a-93a3-f87d9f4d4f86:0:1:1@27:the copy | E3 | yes | yes | yes | "Copy it, then you may cast the" (earlier in the same clause) creates the copy of the card that is then cast, CR 707.12; PRODUCT |
| d514704b-4055-48ed-9da3-e4397fca7576:0:0:1@31:the copy | E3 | yes | yes | yes | "copy it if you gained life this" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| d55f6c70-321f-4fb4-bd33-0850ae1a7c36:0:0:1@31:the copy | E3 | yes | yes | yes | "Copy target instant or sorcery spell, then" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| d6494704-54b2-4c80-acb4-184c9815c5f3:0:0:1@31:the copy | E3 | yes | yes | yes | "Copy target instant or sorcery spell that" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| d6ae77b3-59e7-475c-800c-930a5cb2e0ca:0:2:1@31:the copy | E3 | yes | yes | yes | "copy that ability" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| d85ba214-fa05-44ca-a7f9-ab2c5dc07962:0:1:1@31:the copy | E3 | yes | yes | yes | "copy that spell" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| d85e5398-fa97-4bcd-8b93-008f3f435e22:0:1:2@31:the copy | E3 | yes | yes | yes | "copy that spell" (clause 1, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| d8c95a86-2f05-44f9-8ed7-b1798eaed42f:0:0:2@31:the copy | E3 | yes | yes | yes | "copy that ability" (clause 1, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| da21f1a7-65d0-46d0-8ad1-f84a387ba753:0:1:1@31:the copy | E3 | yes | yes | yes | "Copy target activated or triggered ability you" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| da50989e-4fd4-4353-afd5-9c1354330ec2:0:1:1@24:the copy | E3 | yes | yes | yes | "copy the exiled card" (clause 0, earlier in the paragraph) creates the copy of the card that is then cast, CR 707.12; PRODUCT |
| dcd5ab1b-adc5-486e-a1e0-636af6ee9470:0:1:1@31:the copy | E3 | yes | yes | yes | "copy that ability" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| ddd649f4-dbaf-48ec-8ff7-95581257772d:0:1:1@24:the copy | E3 | yes | yes | yes | "copy the exiled card" (clause 0, earlier in the paragraph) creates the copy of the card that is then cast, CR 707.12; PRODUCT |
| dfd12e3c-2b2a-4461-a08d-09d4e6c4626e:0:3:1@31:the copy | E3 | yes | yes | yes | "Copy target instant or sorcery spell you" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| e1b6d0ab-4e11-43a2-8a7f-3fb51582ddf3:0:1:2@13:the copy | E3 | yes | yes | yes | "Copy it" (clause 1, earlier in the paragraph) creates the copy of the card that is then cast, CR 707.12; PRODUCT |
| e2d21635-182f-4ebf-a6f5-d4c1fd7f9705:0:1:1@31:the copy | E3 | yes | yes | yes | "copy the next spell you cast this" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| e35d4c62-5211-4785-b683-a83719195d87:0:2:2@31:the copy | E3 | yes | yes | yes | "copy it" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| e835da40-f484-4d8b-98de-595cd23b51bc:0:1:1@31:the copy | E3 | yes | yes | yes | "Copy target activated or triggered ability you" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| ea7302b3-c9a2-4bc4-81b8-3a8d1d7c3b8b:0:0:2@31:the copy | E3 | yes | yes | yes | "copy that ability" (clause 1, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| eb7b024c-da9b-4544-8648-0ac0395cf7fc:0:2:2@13:the copy | E3 | yes | yes | yes | "copy it" (clause 1, earlier in the paragraph) creates the copy of the card that is then cast, CR 707.12; PRODUCT |
| ebb88893-427f-496c-82a8-94d2bafb5e4c:0:0:2@13:the copy | E3 | yes | yes | yes | "Copy it" (clause 1, earlier in the paragraph) creates the copy of the card that is then cast, CR 707.12; PRODUCT |
| ec8a4b26-633a-4e88-aa8a-82e9704b3439:0:2:1@31:the copy | E3 | yes | yes | yes | "Copy target instant or sorcery spell you" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| eeb50bfc-8443-482b-bfc1-ea96b37809cd:0:1:2@13:the copy | E3 | yes | yes | yes | "Copy it" (clause 1, earlier in the paragraph) creates the copy of the card that is then cast, CR 707.12; PRODUCT |
| f0bbcabf-29e7-4c7e-893f-86b64d3620a9:1:0:1@31:the copy | E3 | yes | yes | yes | "Copy target activated or triggered ability you" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| f42c0b5b-7a86-4f79-a5d3-859ec25ed870:0:0:2@0:the copy | E3 | yes | yes | yes | "Copy that spell" (clause 1, earlier in the paragraph) creates the copy whose new target the effect specifies, CR 707.10e; PRODUCT |
| f586ecb8-310c-4f40-a766-6a7ca46a254d:0:1:1@31:the copy | E3 | yes | yes | yes | "Copy target instant or sorcery spell" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| f5daadc1-98ff-480a-82bb-fe7bfaa7b60e:0:0:1@31:the copy | E3 | yes | yes | yes | "copy that spell" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| f69574dd-097f-4908-9cab-344b0eb39c62:0:1:1@31:the copy | E3 | yes | yes | yes | "copy that spell" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| f697c78d-7e4f-4320-bfc6-2a25e6d7dc94:0:0:2@31:the copy | E3 | yes | yes | yes | "copy that spell" (clause 1, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| f76bcbfe-483f-4e63-8425-76feca1abf3e:0:0:1@115:the copy | E3 | yes | yes | yes | "copy that spell and you may choose" (earlier in the same clause) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| f9247a6e-2e2d-4125-986b-e03714601e1c:0:1:1@63:the copy | E3 | yes | yes | yes | "copy that spell, and you may choose" (earlier in the same clause) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| fa09e18c-e7cf-4f08-9cc4-324e36594063:0:0:2@0:the copy | E3 | yes | yes | yes | "Copy that spell" (clause 1, earlier in the paragraph) creates the copy whose new target the effect specifies, CR 707.10e; PRODUCT |
| fb98f6b7-5986-4c5d-98fc-e5c4106f48bf:0:3:1@31:the copy | E3 | yes | yes | yes | "Copy target instant or sorcery spell" (clause 0, earlier in the paragraph) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |
| fc6e170c-820c-48bb-95c7-ee79fba634de:0:1:0@61:the copy | E3 | yes | yes | yes | "copy it, except the copy isn't legendary" (earlier in the same clause) creates the copy that the exception modifies, CR 707.9; PRODUCT |
| fc90f74d-11f3-4bd4-b8a1-1cf2ffcd5b73:0:1:1@62:the copy | E3 | yes | yes | yes | "copy that spell and you may choose" (earlier in the same clause) creates the copy whose targets may be changed, CR 707.10c; PRODUCT |

## Verdict

- E3/P2: PASS (rows 98, endpoint-no 0, kind-no 0, duplicate-no 0, cannot-judge 0); every endpoint is the printed copy instruction that creates the copy its reference names, every kind is PRODUCT, and no span overlaps another read-set row.

## Captain questions

None from this part. No row needed a cannot-judge cell, and no rule, word list or window outside I5.3 was needed to judge any row.
