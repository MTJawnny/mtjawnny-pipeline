# M05 read: rule E3, part 1 of 2

refs.json sha256: 497d399005cefd631922aa62ce3298a98a0eb7b4863aae9000e2385502f67e7d

Wave M05-E3-P1.ORACLE-COMPILER-REFERENCE-READ, authority Issue 1 checkpoint 6076415685 task 6051724880, base 209690737dbf16c40b7092657033618cb1a96787.

## Preconditions

- `python3 experiments/oracle_ingest/m05_check.py --protocol` output sha256 is 66e13172e565b21189008995b936a1b5a931dff205ae2f794bca04eb57835873, the planned protocol.
- `git rev-parse HEAD:oracle_compiler/INTERFACES.md` is 282c295c03f2a4b43e723d01710baaf479aa716c (oracle-compiler-interface/5).
- c04_refs.py, h_region.py, h_region_kill.py, m05_check.py and INTERFACES.md are unchanged from the C04 accepted head b3b686b3804d0d4bf533e066606c646542ccdc38 (empty `git diff`).
- Hand-off rule: refs.json existed, so `python3 experiments/oracle_ingest/c04_refs.py --verify` ran first and reported every embedded hash current (19 files), not stale. Its sha256 above equals the operator copy refs-497d3990.json.

## Reader and method

- Reader: a fresh, isolated headless Claude session. It is neither the C04 Worker nor the author of the rules. Rules are frozen: no rule, refs.json or c04_refs.py was edited. Scratch files from earlier sessions in the ignored output directory were not opened.
- Rows: rule E3 (copy-product, CR 707.10) has 208 candidates in refs.json, 196 of them RESOLVED. This matches the §I5.4 total, re-derived from refs.json rather than trusted. Sorted by (class, row_id) and split at P 2, part 1 holds rows 0 to 97, 98 rows, all of class E3. The ledger order is the order printed by `m05_check.py --skeleton --rule E3 --part 1`.
- Cards first: for every row the reader read paragraph_text, ref_text and endpoint_text and decided what the reference means before looking at the recorded endpoint. Every row was read; none was sampled or inferred from a neighbouring row.
- Rules applied: CR 707.10 for copies of spells and abilities, which are put onto the stack as new objects, and 707.10c for choosing new targets for the copy. CR 707.12 for copies of cards that are then cast. In each row the reference names the object made by the paragraph's single earlier copy instruction, so the endpoint clause is the clause that prints that instruction, and the kind is PRODUCT.
- Paragraph shapes seen: a copy instruction followed by a separate clause about new targets for the copy (the common shape). An except-clause in the same clause as the instruction. A conjoined clause in the same clause. A following clause that casts the copy of a card. Delayed when-you-next-cast instructions. Conditional if-you-do instructions. Ledger rows whose clause offset is 0 print the phrase capitalised. That is a case difference only; the span is the same.
- DUPLICATE: no refs.json candidate, of any rule or outcome, at the same clause address claims a span intersecting any row of this part. That was checked over all 5856 candidates. Each row's own text was also read for a second reference at the same span, and none was found.
- Every note quotes, verbatim from the row's endpoint_text (also present in its paragraph_text), the copy instruction the reference points to.

## Ledger

| row | class | endpoint | kind | duplicate | note |
|---|---|---|---|---|---|
| 005354c1-7ee5-498d-87b7-b12cfb9ec12c:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy it" in endpoint clause 0:1:0; CR 707.10 |
| 04853f06-3fd2-445d-9b0d-d68d0f116635:0:1:2@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that ability" in endpoint clause 0:1:1; CR 707.10 |
| 04c6aa4e-b328-44b8-9d47-3c0d10289048:0:1:2@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell" in endpoint clause 0:1:1; CR 707.10 |
| 0727dc95-03df-4a2c-aed5-73fb840f3db7:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target activated or triggered ability you control from a colorless source" in endpoint clause 0:1:0; CR 707.10 |
| 08bb1f33-b232-4382-a268-4804d4e72d29:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target instant or sorcery spell you control with mana value X" in endpoint clause 0:1:0; CR 707.10 |
| 08dd393f-12d8-4801-882c-6d76009b4f12:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy the spell countered this way" in endpoint clause 0:1:0; CR 707.10 |
| 095d9719-0db6-43de-8e4f-a0035a4c65ed:0:2:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy it" in endpoint clause 0:2:0; CR 707.10 |
| 0a66ce8b-af99-411f-8ecb-52a5d2f6af3d:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that ability" in endpoint clause 0:1:0; CR 707.10 |
| 0af6f3ce-59e8-4797-aa1b-dbdb5288fe3d:0:2:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that ability" in endpoint clause 0:2:0; CR 707.10 |
| 0bf299da-1854-4153-baea-3cee2eb01ee8:0:0:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target activated or triggered ability you control" in endpoint clause 0:0:0; CR 707.10 |
| 0bf299da-1854-4153-baea-3cee2eb01ee8:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target instant or sorcery spell you control" in endpoint clause 0:1:0; CR 707.10 |
| 0c85a577-db82-4a36-bc42-49644eba1cf2:0:1:0@241:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell" in same clause 0:1:0; CR 707.10 |
| 0e3cb267-5704-4708-94c8-e2fbce4978af:0:1:2@13:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy that card" in endpoint clause 0:1:1; CR 707.12, copy of a card then cast |
| 0ebe67ed-8a71-4bbc-8e58-cebbd7b2d83f:0:0:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell or ability" in endpoint clause 0:0:0; CR 707.10 |
| 0eff910a-712d-4652-8b3b-9eddf63eb891:0:3:2@13:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy it" in endpoint clause 0:3:1; CR 707.12, copy of a card then cast |
| 0f0282c6-aceb-4879-8ec8-482d0501204a:0:2:0@68:the copy | E3 | yes | yes | yes | the copy is the object made by "copy it" in same clause 0:2:0; CR 707.10 |
| 10777360-c046-43e3-ab44-9d0b926fbbf8:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target activated or triggered ability you control" in endpoint clause 0:1:0; CR 707.10 |
| 10891656-070f-49f4-80e0-78061b773f17:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target instant or sorcery spell you control" in endpoint clause 0:1:0; CR 707.10 |
| 1091c83a-a4b9-457f-a69a-9a44a7e10759:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target activated or triggered ability you control from a creature source" in endpoint clause 0:1:0; CR 707.10 |
| 144d0817-348c-4171-aa7e-3468b23cf97d:0:2:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target spell" in endpoint clause 0:2:0; CR 707.10 |
| 158a6225-a246-4fd6-aa57-0df8067b4383:0:2:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy target instant or sorcery spell you control" in endpoint clause 0:2:0; CR 707.10 |
| 16414460-11ce-481d-ab54-6f0e0ea7d83d:0:3:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target instant or sorcery spell you control" in endpoint clause 0:3:0; CR 707.10 |
| 18e421c0-2879-4ad8-b027-397f168dfbc2:0:0:2@73:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell" in same clause 0:0:2; CR 707.10 |
| 195bd8fe-581c-44ed-b7f8-e800df3502ff:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy it" in endpoint clause 0:1:0; CR 707.10 |
| 1b9f9f5b-8712-4f00-90cb-1b7b9970eccc:0:0:1@97:the copy | E3 | yes | yes | yes | the copy is the object made by "copy this spell and may choose a new target for the copy" in same clause 0:0:1; CR 707.10 |
| 1c3e6980-97fe-4e15-93a0-368280da8608:0:1:1@13:the copy | E3 | yes | yes | yes | the copy is the object made by "copy it" in endpoint clause 0:1:0; CR 707.12, copy of a card then cast |
| 1c9f2b6e-a0eb-493e-8c43-3a14f6d95a53:0:0:0@85:the copy | E3 | yes | yes | yes | the copy is the object made by "copy it" in same clause 0:0:0; CR 707.10 |
| 1d1d78af-7982-419d-b9be-2bf4c149d97d:0:0:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that ability" in endpoint clause 0:0:0; CR 707.10 |
| 1d55a1c5-fd0b-44d2-9e7c-550052fef262:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy the next instant or sorcery spell you cast this turn when" in endpoint clause 0:1:0; CR 707.10 |
| 1fd733a3-95bb-4b23-920e-e3f48a824fa5:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy it" in endpoint clause 0:1:0; CR 707.10 |
| 2158c73d-421b-4c94-af06-dd89cb8d3126:0:1:1@88:the copy | E3 | yes | yes | yes | the copy is the object made by "copy it and you may choose new targets for the copy" in same clause 0:1:1; CR 707.10 |
| 23a79523-4be0-4d17-80aa-5ea024cb3463:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy it" in endpoint clause 0:1:0; CR 707.10 |
| 23e6df25-90db-42a4-8658-e592e67be15e:0:2:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target spell you control that wasn't cast" in endpoint clause 0:2:0; CR 707.10 |
| 23f01235-b5a5-4b2e-a90b-b49fc0c7b18d:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that ability" in endpoint clause 0:1:0; CR 707.10 |
| 2469c0b7-a045-4733-bf53-28f3fdbe3797:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy it" in endpoint clause 0:1:0; CR 707.10 |
| 24a7e1d2-0bc9-40a9-a606-f0017bde3dab:0:1:1@62:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell and you may choose new targets for the copy" in same clause 0:1:1; CR 707.10 |
| 24a7e1d2-0bc9-40a9-a606-f0017bde3dab:0:1:2@3:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell and you may choose new targets for the copy" in endpoint clause 0:1:1; CR 707.10 |
| 2631130e-63e2-43a3-914a-648e76722203:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell" in endpoint clause 0:1:0; CR 707.10 |
| 2a7504b9-220d-412e-9381-b6a8a3750241:0:1:2@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy it" in endpoint clause 0:1:1; CR 707.10 |
| 2b08e5f7-c771-4e03-8560-15de6a8bec71:0:0:2@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell" in endpoint clause 0:0:1; CR 707.10 |
| 30377bd5-99ab-4888-9ea7-e5a069b527e8:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target instant spell" in endpoint clause 0:1:0; CR 707.10 |
| 31af65c3-602b-4ac9-a25f-dccb88f8f751:0:1:2@13:the copy | E3 | yes | yes | yes | the copy is the object made by "copy it" in endpoint clause 0:1:1; CR 707.12, copy of a card then cast |
| 322e3bc1-2dfa-4d5f-848f-a82d9ce02a67:0:3:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell" in endpoint clause 0:3:0; CR 707.10 |
| 34778e85-cd02-40c8-855c-4f4529aa458b:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target instant spell you control with mana value 2 or less" in endpoint clause 0:1:0; CR 707.10 |
| 34778e85-cd02-40c8-855c-4f4529aa458b:0:2:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target sorcery spell you control with mana value 2 or less" in endpoint clause 0:2:0; CR 707.10 |
| 36d6d6c0-721c-40c3-b81f-4f027fcf847e:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy it" in endpoint clause 0:1:0; CR 707.10 |
| 370d67f6-8d43-46ca-ae6c-00799bb0bd0c:0:0:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy it" in endpoint clause 0:0:0; CR 707.10 |
| 371fa9e3-5432-4f2f-89d4-55061b0b4e57:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target instant or sorcery spell" in endpoint clause 0:1:0; CR 707.10 |
| 3735559f-efe5-43ad-9b3e-3ef127c0ceda:0:0:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target instant or sorcery spell you control" in endpoint clause 0:0:0; CR 707.10 |
| 38394ee3-6726-4f91-bc25-36bce0c6aab9:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target instant or sorcery spell" in endpoint clause 0:1:0; CR 707.10 |
| 3a272fa9-5f28-43a4-95de-10cb511f1b43:0:0:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target triggered ability you control" in endpoint clause 0:0:0; CR 707.10 |
| 3c067dbb-934b-4ebb-a656-8541349a4b2a:0:0:2@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell" in endpoint clause 0:0:1; CR 707.10 |
| 3ca8113b-f5b8-41a7-aae6-ebb32554dfe3:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target instant or sorcery spell you control" in endpoint clause 0:1:0; CR 707.10 |
| 3d177c04-9aa3-44b8-bbe4-df5de23a4ce6:0:0:1@63:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy it" in same clause 0:0:1; CR 707.10 |
| 3d92e5ce-9d30-4203-9f84-6c36117440cf:0:1:1@13:the copy | E3 | yes | yes | yes | the copy is the object made by "copy the enchanted instant card" in endpoint clause 0:1:0; CR 707.12, copy of a card then cast |
| 40362fe0-a1a9-4d76-8c35-eac474b91af5:0:0:1@57:the copy | E3 | yes | yes | yes | the copy is the object made by "copy it" in same clause 0:0:1; CR 707.12, copy of a card then cast |
| 40ed32a6-ad56-48c7-aecf-b4238c34c212:0:1:0@144:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell if it targets a permanent or player" in same clause 0:1:0; CR 707.10 |
| 41d11144-32fc-4e45-a8db-3edb9dc0ce80:0:1:1@89:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that card and you may cast the copy" in same clause 0:1:1; CR 707.12, copy of a card then cast |
| 4563ae4b-6226-4cc9-abde-582d0ab83433:0:0:1@106:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell" in same clause 0:0:1; CR 707.10 |
| 48cce741-cfbd-4ed9-a7ac-38880867a286:0:0:0@74:the copy | E3 | yes | yes | yes | the copy is the object made by "copy it" in same clause 0:0:0; CR 707.10 |
| 494b31b2-27ef-4ca1-ac72-c2fcfc8a23a1:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target activated or triggered ability you control from an enchantment source" in endpoint clause 0:1:0; CR 707.10 |
| 49bfecc3-6258-454e-a8fd-fc49098a0898:0:2:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy it" in endpoint clause 0:2:0; CR 707.10 |
| 49cb8d81-d8a0-4ae7-9750-6788a3e9c81b:0:0:0@78:the copy | E3 | yes | yes | yes | the copy is the object made by "copy it" in same clause 0:0:0; CR 707.10 |
| 4a7a5ea9-b633-459f-bcd4-40de53afce0e:0:0:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell" in endpoint clause 0:0:0; CR 707.10 |
| 4c340b82-22e1-445a-b236-82471b442031:0:1:1@0:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell" in endpoint clause 0:1:0; CR 707.10 |
| 4db030f5-d7c4-4aa0-ae2e-12943e2683d7:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell or ability" in endpoint clause 0:1:0; CR 707.10 |
| 4f0c3154-1917-4bb5-9ba2-446943a88808:0:1:3@13:the copy | E3 | yes | yes | yes | the copy is the object made by "copy the exiled card" in endpoint clause 0:1:2; CR 707.12, copy of a card then cast |
| 505cb78d-b292-4d16-b3f2-110164b4cc93:0:1:1@24:the copy | E3 | yes | yes | yes | the copy is the object made by "copy a card exiled with this artifact" in endpoint clause 0:1:0; CR 707.12, copy of a card then cast |
| 50c53ae0-51ba-4046-ac74-87c65e688032:0:0:0@50:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target instant or sorcery spell" in same clause 0:0:0; CR 707.10 |
| 50c53ae0-51ba-4046-ac74-87c65e688032:0:0:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target instant or sorcery spell" in endpoint clause 0:0:0; CR 707.10 |
| 529f259a-df66-4283-bc28-de3933c42e67:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy it" in endpoint clause 0:1:0; CR 707.10 |
| 52ec472e-a745-4e25-b9a7-8e1eb8873594:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell" in endpoint clause 0:1:0; CR 707.10 |
| 53231b31-fb3c-4b30-bfe9-0ee8e754247b:0:0:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy it" in endpoint clause 0:0:0; CR 707.10 |
| 532ff38d-bf52-4e99-bf1c-254074e4d625:0:0:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target instant or sorcery spell" in endpoint clause 0:0:0; CR 707.10 |
| 536c1112-694f-42f8-a7b1-604389e54a95:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell" in endpoint clause 0:1:0; CR 707.10 |
| 5482ddb1-7f7d-492a-aa3d-67c037062cc3:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target spell you control" in endpoint clause 0:1:0; CR 707.10 |
| 55ad6a6b-1c44-4397-86ae-dd9221892b22:0:1:1@0:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell" in endpoint clause 0:1:0; CR 707.10 |
| 562c9c68-e5a7-45ab-b098-5b649d165ff5:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy target instant or sorcery spell you control" in endpoint clause 0:1:0; CR 707.10 |
| 56528234-46c0-4fba-972a-0c8011996f8d:0:3:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy it" in endpoint clause 0:3:0; CR 707.10 |
| 566533af-5e67-463f-ac33-dfcf1ec735c9:0:0:2@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell" in endpoint clause 0:0:1; CR 707.10 |
| 57b86d5c-3269-44bc-a838-3c5439d820d9:0:2:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target instant or sorcery spell you control" in endpoint clause 0:2:0; CR 707.10 |
| 5998f07e-01f9-4d02-94dd-867c7166463f:0:1:0@95:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell" in same clause 0:1:0; CR 707.10 |
| 5b90f8ed-84b2-4306-9dfa-b5654ea0e4cd:0:2:2@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell" in endpoint clause 0:2:1; CR 707.10 |
| 5bc3c4e2-087d-4255-a576-0b17ed1e8c3f:0:1:1@13:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy the exiled card" in endpoint clause 0:1:0; CR 707.12, copy of a card then cast |
| 5f725d51-e133-488c-9ca9-1c7b0523b5bd:0:0:4@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy the spell" in endpoint clause 0:0:3; CR 707.10 |
| 61495793-b0c7-40a5-ad3e-9df8e2b8096b:0:2:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target instant or sorcery spell you control" in endpoint clause 0:2:0; CR 707.10 |
| 61495793-b0c7-40a5-ad3e-9df8e2b8096b:0:3:1@0:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target creature spell you control" in endpoint clause 0:3:0; CR 707.10 |
| 61be7df8-cc78-4822-9e70-f226a8a96c9d:0:3:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy that spell" in endpoint clause 0:3:0; CR 707.10 |
| 63d50d5e-56de-44c4-b906-b2a21a56e3f3:0:0:2@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell" in endpoint clause 0:0:1; CR 707.10 |
| 6556c4c0-b10d-4208-821b-0c0a49abd188:0:0:2@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell" in endpoint clause 0:0:1; CR 707.10 |
| 6629a48b-be9a-4636-8add-69d096a1ca7e:0:0:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell" in endpoint clause 0:0:0; CR 707.10 |
| 6b8c69ac-1856-4070-9489-798a6b224268:0:1:1@13:the copy | E3 | yes | yes | yes | the copy is the object made by "copy a card you exiled with cards named ~" in endpoint clause 0:1:0; CR 707.12, copy of a card then cast |
| 70e10cb9-ae27-4dba-9a0d-34a78f924774:0:0:2@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell" in endpoint clause 0:0:1; CR 707.10 |
| 73c7fdb3-4742-4d08-8658-daa4435c49b1:1:0:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy target spell you control" in endpoint clause 1:0:0; CR 707.10 |
| 740fe41a-16bb-4c97-a03c-f678f15a0a0c:0:1:1@13:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy that card" in endpoint clause 0:1:0; CR 707.12, copy of a card then cast |
| 740fe41a-16bb-4c97-a03c-f678f15a0a0c:0:2:1@13:the copy | E3 | yes | yes | yes | the copy is the object made by "Copy that card" in endpoint clause 0:2:0; CR 707.12, copy of a card then cast |
| 76d9c310-9d06-43e8-87a9-fb03318a6cb8:0:0:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell" in endpoint clause 0:0:0; CR 707.10 |
| 76d9c310-9d06-43e8-87a9-fb03318a6cb8:0:1:1@31:the copy | E3 | yes | yes | yes | the copy is the object made by "copy that spell an additional time" in endpoint clause 0:1:0; CR 707.10 |

## Verdict

- E3/P1: PASS (rows 98, endpoint-no 0, kind-no 0, duplicate-no 0, cannot-judge 0); every recorded endpoint is the clause printing the copy instruction whose product the reference names, kind PRODUCT throughout, no intersecting spans.

## Captain questions

None. The part has no endpoint-no, kind-no, duplicate-no or cannot-judge row, so there is nothing to escalate.
