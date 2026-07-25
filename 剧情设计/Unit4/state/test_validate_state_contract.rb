# frozen_string_literal: true

require "fileutils"
require "json"
require "minitest/autorun"
require "tmpdir"

VALIDATOR_PATH = File.expand_path("validate_state_contract.rb", __dir__)

unless File.exist?(VALIDATOR_PATH)
  class Unit4StateValidatorMissingTest < Minitest::Test
    def test_validator_exists
      assert File.exist?(VALIDATOR_PATH),
             "validate_state_contract.rb must exist before contract behavior can be tested"
    end
  end
else
  require_relative "validate_state_contract"

  class Unit4StateContractTest < Minitest::Test
    REPO_ROOT = File.expand_path("../../..", __dir__)

    def setup
      @tmpdir = Dir.mktmpdir("unit4-state-contract-")
      FileUtils.cp(File.join(REPO_ROOT, "canon_manifest.json"), @tmpdir)
      source = File.join(REPO_ROOT, "剧情设计", "Unit4", "state")
      target = File.join(@tmpdir, "剧情设计", "Unit4", "state")
      FileUtils.mkdir_p(File.dirname(target))
      FileUtils.cp_r(source, target)
      unit5_source = File.join(REPO_ROOT, "剧情设计", "Unit5", "Unit5_大纲_0601.md")
      unit5_target = File.join(@tmpdir, "剧情设计", "Unit5", "Unit5_大纲_0601.md")
      FileUtils.mkdir_p(File.dirname(unit5_target))
      FileUtils.cp(unit5_source, unit5_target)
    end

    def teardown
      FileUtils.remove_entry(@tmpdir) if @tmpdir && File.exist?(@tmpdir)
    end

    def test_repository_state_satisfies_contract
      assert_empty validate.errors
    end

    def test_rejects_custom_scene_type
      mutate(
        "loop1_state.yaml",
        "type: cutscene\n    design_tags",
        "type: opening_cutscene\n    design_tags"
      )

      assert_error_includes("scene type")
    end

    def test_rejects_custom_ending_scene_type
      mutate(
        "loop5_state.yaml",
        "      type: cutscene\n      design_tags: [transition, aftermath]",
        "      type: story_transition\n      design_tags: [transition, aftermath]"
      )

      assert_error_includes("scene type")
    end

    def test_rejects_unapproved_design_tag
      mutate(
        "loop1_state.yaml",
        "design_tags: [opening, transition]",
        "design_tags: [opening, transition, no_player_control]"
      )

      assert_error_includes("design tag")
    end

    def test_rejects_unclassified_top_level_field
      append("loop1_state.yaml", "\nunclassified_runtime_guess: true\n")

      assert_error_includes("unclassified top-level field")
    end

    def test_rejects_invalid_field_policy_category
      mutate_contract("scenes: runtime_source", "scenes: arbitrary_typo")

      assert_error_includes("field policy")
    end

    def test_rejects_tampered_persistence_contract
      mutate_contract(
        "  - id: 4112\n    source_loop: 1",
        "  - id: 4999\n    source_loop: 1"
      )

      assert_error_includes("approved persistence contract")
    end

    def test_rejects_synchronized_identity_contract_rollback
      mutate_contract(
        "  status: approved_provisional_ui",
        "  status: provisional"
      )
      mutate(
        "loop5_state.yaml",
        "status: approved_provisional_ui",
        "status: provisional"
      )

      assert_error_includes("approved identity contract")
    end

    def test_rejects_synchronized_manifest_loop_expansion
      mutate_contract("expected_loops: 5", "expected_loops: 6")
      manifest_path = File.join(@tmpdir, "canon_manifest.json")
      manifest = JSON.parse(File.read(manifest_path, encoding: "UTF-8"))
      unit4 = manifest.fetch("chapters").find { |entry| entry["canonicalUnit"] == "Unit4" }
      unit4.fetch("maturity").fetch("state")["expectedLoops"] = 6
      File.write(manifest_path, JSON.pretty_generate(manifest), mode: "w:UTF-8")

      assert_error_includes("approved manifest contract")
    end

    def test_rejects_synchronized_scene_type_expansion
      mutate_contract(
        "scene_types:\n  - cutscene\n  - free_exploration",
        "scene_types:\n  - cutscene\n  - free_exploration\n  - story_transition"
      )
      mutate(
        "loop5_state.yaml",
        "      type: cutscene\n      design_tags: [transition, aftermath]",
        "      type: story_transition\n      design_tags: [transition, aftermath]"
      )

      assert_error_includes("approved scene type contract")
    end

    def test_rejects_synchronized_non_progress_blocking
      mutate_contract("    blocking: false", "    blocking: true")
      mutate_all("loop3_state.yaml", "      blocking: false", "      blocking: true")

      assert_error_includes("approved non-progress contract")
    end

    def test_rejects_synchronized_early_chapter_end
      mutate_contract(
        "chapter_end_after: ending_4045",
        "chapter_end_after: ending_4044"
      )
      mutate(
        "loop5_state.yaml",
        "chapter_end_after: ending_4045",
        "chapter_end_after: ending_4044"
      )

      assert_error_includes("approved ending contract")
    end

    def test_rejects_broken_known_facts_inheritance
      mutate(
        "loop2_state.yaml",
        "Harrison 长期收受 1919-A 资金",
        "Harrison 从未收受 1919-A 资金"
      )

      assert_error_includes("known facts inheritance")
    end

    def test_rejects_identity_lock_open_questions
      mutate(
        "loop5_state.yaml",
        "replaces_standard_doubts: true",
        "replaces_standard_doubts: true\n    open_questions: [ui_layout]"
      )

      assert_error_includes("open_questions")
    end

    def test_rejects_identity_lock_status_drift
      mutate(
        "loop5_state.yaml",
        "status: approved_provisional_ui",
        "status: provisional"
      )

      assert_error_includes("identity_lock status")
    end

    def test_rejects_non_parallel_identity_lanes
      mutate("loop5_state.yaml", "lanes: parallel", "lanes: sequential")

      assert_error_includes("identity_lock lanes")
    end

    def test_rejects_free_form_identity_slots
      mutate("loop5_state.yaml", "slots: fixed_per_chain", "slots: free_form")

      assert_error_includes("identity_lock slots")
    end

    def test_rejects_early_mickey_return
      mutate(
        "loop5_state.yaml",
        'condition: "special_mechanics.identity_lock.completion_condition 达成"',
        'condition: "always"'
      )

      assert_error_includes("mickey_returns")
    end

    def test_rejects_ordinary_doubt_expose_bypass
      mutate(
        "loop5_state.yaml",
        'unlock_condition: "special_mechanics.identity_lock.completion_condition == all_chains_completed"',
        'unlock_condition: "ordinary_doubts_complete OR special_mechanics.identity_lock.completion_condition == all_chains_completed"'
      )

      assert_error_includes("expose unlock condition")
    end

    def test_rejects_standard_doubt_gate_for_loop5
      mutate(
        "loop5_state.yaml",
        "standard_doubt_progress_required: false",
        "standard_doubt_progress_required: true"
      )

      assert_error_includes("standard doubt progress")
    end

    def test_rejects_missing_chapter_persistence
      mutate("loop1_state.yaml", "scope: chapter", "scope: loop")

      assert_error_includes("persistence")
    end

    def test_rejects_wrong_reset_policy
      mutate(
        "loop1_state.yaml",
        "reset_policy: retain_across_loops",
        "reset_policy: discard_on_reset"
      )

      assert_error_includes("persistence")
    end

    def test_rejects_missing_identity_chain_consumer
      mutate(
        "loop5_state.yaml",
        "id: 4112\n            name: \"1919-A入账存根\"",
        "id: 4998\n            name: \"1919-A入账存根\""
      )

      assert_error_includes("persistence consumer")
    end

    def test_rejects_wrong_safe_input_source
      mutate("loop5_state.yaml", "input_source: 4418", "input_source: 4998")

      assert_error_includes("persistence consumer")
    end

    def test_rejects_blocking_non_progress_record
      mutate("loop3_state.yaml", "blocking: false", "blocking: true")

      assert_error_includes("non-progress record")
    end

    def test_rejects_non_progress_record_in_doubt_progress
      append(
        "loop3_state.yaml",
        "\ndoubt_progress:\n  denominator: 4\n  inputs: [record_suicide_scene]\n"
      )

      assert_error_includes("non-progress record enters ordinary progress")
    end

    def test_rejects_non_progress_record_in_expose_expression
      mutate(
        "loop3_state.yaml",
        "  unlock_condition:\n    doubts_completed: [4301, 4302, 4303]",
        '  unlock_condition: "record_suicide_scene == complete"'
      )

      assert_error_includes("non-progress record enters ordinary progress")
    end

    def test_rejects_premature_chapter_end
      mutate(
        "loop5_state.yaml",
        "chapter_end_after: ending_4045",
        "chapter_end_after: ending_4044"
      )

      assert_error_includes("chapter_end_after")
    end

    def test_rejects_early_ending_scene_chapter_end
      mutate(
        "loop5_state.yaml",
        "    - id: ending_4043\n      scene_id: 4043",
        "    - id: ending_4043\n      chapter_end: true\n      scene_id: 4043"
      )

      assert_error_includes("early ending scene")
    end

    def test_rejects_wrong_unit5_first_action
      mutate(
        "loop5_state.yaml",
        'unit5_first_allowed_action: "进入 O\'Hara 家并开始屋内救援"',
        'unit5_first_allowed_action: "直接前往医院质问"'
      )

      assert_error_includes("unit5 first allowed action")
    end

    def test_rejects_wrong_unit5_outline_first_action
      path = File.join(@tmpdir, "剧情设计", "Unit5", "Unit5_大纲_0601.md")
      text = File.read(path, encoding: "UTF-8")
      old_text = "- Zack 与 Emma 进入屋内，确认 O'Hara"
      assert_includes text, old_text
      File.write(
        path,
        text.sub(old_text, "- Zack 与 Emma 直接前往医院，随后确认 O'Hara"),
        mode: "w:UTF-8"
      )

      assert_error_includes("Unit5 active outline")
    end

    def test_missing_manifest_returns_readable_error
      FileUtils.rm(File.join(@tmpdir, "canon_manifest.json"))

      assert_error_includes("canon_manifest.json")
    end

    private

    def state_path(name)
      File.join(@tmpdir, "剧情设计", "Unit4", "state", name)
    end

    def contract_path
      state_path("state_contract.yaml")
    end

    def mutate(name, old_text, new_text)
      path = state_path(name)
      text = File.read(path, encoding: "UTF-8")
      assert_includes text, old_text, "fixture mutation target missing: #{old_text}"
      File.write(path, text.sub(old_text, new_text), mode: "w:UTF-8")
    end

    def mutate_all(name, old_text, new_text)
      path = state_path(name)
      text = File.read(path, encoding: "UTF-8")
      assert_includes text, old_text, "fixture mutation target missing: #{old_text}"
      File.write(path, text.gsub(old_text, new_text), mode: "w:UTF-8")
    end

    def append(name, text)
      File.open(state_path(name), "a:UTF-8") { |file| file.write(text) }
    end

    def mutate_contract(old_text, new_text)
      text = File.read(contract_path, encoding: "UTF-8")
      assert_includes text, old_text, "contract mutation target missing: #{old_text}"
      File.write(contract_path, text.sub(old_text, new_text), mode: "w:UTF-8")
    end

    def validate
      Unit4StateContract::Validator.new(root: @tmpdir).validate
    end

    def assert_error_includes(fragment)
      assert validate.errors.any? { |error| error.include?(fragment) },
             "expected an error containing #{fragment.inspect}, got: #{validate.errors.inspect}"
    end
  end
end
