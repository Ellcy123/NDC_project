# frozen_string_literal: true

require "json"
require "psych"
require "yaml"

module Unit4StateContract
  Result = Struct.new(:errors, keyword_init: true)

  class Validator
    STATE_RELATIVE_PATH = File.join("剧情设计", "Unit4", "state")
    APPROVED_CONTRACT_HEADER = {"version" => 1, "unit" => "Unit4"}.freeze
    APPROVED_MANIFEST_CONTRACT = {
      "expected_loops" => 5,
      "structure" => "5_loops_plus_non_loop_finale"
    }.freeze
    ALLOWED_FIELD_POLICIES = %w[runtime_source design_only special_adapter structural].freeze
    APPROVED_FIELD_POLICY = {
      "meta" => "design_only",
      "player_context" => "design_only",
      "opening" => "structural",
      "scenes" => "runtime_source",
      "expose" => "runtime_source",
      "doubts" => "runtime_source",
      "doubt_progress" => "design_only",
      "cross_loop_evidence" => "design_only",
      "evidence_registry" => "runtime_source",
      "testimony_registry" => "runtime_source",
      "non_progress_investigation_records" => "design_only",
      "special_mechanics" => "special_adapter",
      "ending_sequence" => "special_adapter"
    }.freeze
    APPROVED_DESIGN_TAGS = %w[
      opening transition analysis crisis aftermath action_result expose_location
      locked identity_lock story_climax
    ].freeze
    APPROVED_SCENE_TYPES = %w[cutscene free_exploration].freeze
    APPROVED_PERSISTENT_INPUTS = [
      {
        "id" => 4112,
        "source_loop" => 1,
        "registry" => "evidence_registry",
        "required_by" => ["identity_lock.chain_4501"]
      },
      {
        "id" => 4_153_001,
        "source_loop" => 3,
        "registry" => "testimony_registry",
        "required_by" => ["identity_lock.chain_4503"]
      },
      {
        "id" => 4315,
        "source_loop" => 3,
        "registry" => "evidence_registry",
        "required_by" => ["identity_lock.chain_4503"]
      },
      {
        "id" => 4416,
        "source_loop" => 4,
        "registry" => "evidence_registry",
        "required_by" => ["identity_lock.chain_4501"]
      },
      {
        "id" => 4418,
        "source_loop" => 4,
        "registry" => "evidence_registry",
        "required_by" => ["interaction_letter_safe"]
      }
    ].freeze
    APPROVED_IDENTITY_CONTRACT = {
      "loop" => 5,
      "status" => "approved_provisional_ui",
      "chain_ids" => [4501, 4502, 4503],
      "lanes" => "parallel",
      "slots" => "fixed_per_chain",
      "chain_open_order" => "simultaneous",
      "submission" => "player_confirm",
      "completion_condition" => "all_chains_completed",
      "unlocks" => "expose",
      "standard_doubt_progress_required" => false,
      "mickey_returns_condition" => "special_mechanics.identity_lock.completion_condition 达成",
      "expose_unlock_condition" => "special_mechanics.identity_lock.completion_condition == all_chains_completed",
      "wrong_submission" => {
        "consumes_evidence" => false,
        "resets_completed_chains" => false,
        "first_feedback" => "logic_dimension_only",
        "repeated_feedback" => "missing_dimension_only",
        "reveal_correct_id" => false
      }
    }.freeze
    APPROVED_NON_PROGRESS_CONTRACT = {
      "loop" => 3,
      "ids" => %w[
        record_suicide_scene record_forged_note record_gas_timing record_pierce_schedule
      ],
      "presentation" => {
        "channel" => "investigation_log",
        "blocking" => false,
        "auto_unlock" => true,
        "show_completion_toast" => false
      }
    }.freeze
    APPROVED_ENDING_CONTRACT = {
      "owner_loop" => 5,
      "counts_as_loop" => false,
      "chapter_end_after" => "ending_4045",
      "next_unit_entry" => "enter_ohara_house",
      "unit5_first_allowed_action" => "进入 O'Hara 家并开始屋内救援",
      "unit5_outline_first_action_prefix" => "Zack 与 Emma 进入屋内"
    }.freeze

    def initialize(root:)
      @root = File.expand_path(root)
      @state_dir = File.join(@root, STATE_RELATIVE_PATH)
      @errors = []
    end

    def validate
      @errors = []
      load_documents
      return Result.new(errors: @errors) unless @contract && @states&.length == 5 && @manifest

      validate_duplicate_keys
      validate_manifest
      validate_contract_schema
      validate_known_facts_chain
      validate_field_policy
      validate_scene_types
      validate_identity_lock
      validate_persistence
      validate_non_progress_records
      validate_ending_sequence

      Result.new(errors: @errors)
    end

    private

    def load_documents
      contract_path = File.join(@state_dir, "state_contract.yaml")
      unless File.exist?(contract_path)
        @errors << "missing state contract: #{contract_path}"
        return
      end

      @contract = YAML.load_file(contract_path)
      @states = {}
      (1..5).each do |loop_number|
        path = state_path(loop_number)
        if File.exist?(path)
          @states[loop_number] = YAML.load_file(path)
        else
          @errors << "missing loop state: #{path}"
        end
      rescue Psych::SyntaxError => e
        @errors << "invalid YAML in loop#{loop_number}: #{e.message}"
      end

      manifest_path = File.join(@root, "canon_manifest.json")
      @manifest = JSON.parse(File.read(manifest_path, encoding: "UTF-8"))
    rescue Psych::SyntaxError => e
      @errors << "invalid state contract YAML: #{e.message}"
    rescue JSON::ParserError, Errno::ENOENT => e
      @errors << "invalid or missing canon_manifest.json: #{e.message}"
    end

    def validate_duplicate_keys
      [File.join(@state_dir, "state_contract.yaml"), *(1..5).map { |n| state_path(n) }].each do |path|
        next unless File.exist?(path)

        document = Psych.parse_file(path)
        scan_duplicate_keys(document.root, File.basename(path), "$")
      rescue Psych::SyntaxError => e
        @errors << "invalid YAML while checking duplicate keys in #{File.basename(path)}: #{e.message}"
      end
    end

    def scan_duplicate_keys(node, file, path)
      return unless node

      case node
      when Psych::Nodes::Mapping
        seen = {}
        node.children.each_slice(2) do |key_node, value_node|
          key = key_node.respond_to?(:value) ? key_node.value : key_node.to_s
          @errors << "duplicate YAML key in #{file} at #{path}: #{key}" if seen[key]
          seen[key] = true
          scan_duplicate_keys(value_node, file, "#{path}.#{key}")
        end
      when Psych::Nodes::Sequence, Psych::Nodes::Document, Psych::Nodes::Stream
        node.children.each_with_index { |child, index| scan_duplicate_keys(child, file, "#{path}[#{index}]") }
      end
    end

    def validate_manifest
      chapter = Array(@manifest["chapters"]).find { |entry| entry["canonicalUnit"] == "Unit4" }
      unless chapter
        @errors << "canon manifest has no Unit4 chapter"
        return
      end

      state = chapter.dig("maturity", "state") || {}
      expected = @contract.dig("manifest", "expected_loops")
      structure = @contract.dig("manifest", "structure")
      @errors << "manifest expectedLoops must be #{expected}" unless state["expectedLoops"] == expected
      unless chapter.dig("maturity", "structure") == structure
        @errors << "manifest Unit4 structure must be #{structure}"
      end
      @errors << "loop6_state.yaml must not exist for Unit4" if File.exist?(state_path(6))
    end

    def validate_contract_schema
      header = {"version" => @contract["version"], "unit" => @contract["unit"]}
      unless header == APPROVED_CONTRACT_HEADER
        @errors << "approved Unit4 contract header has been changed"
      end
      unless @contract["manifest"] == APPROVED_MANIFEST_CONTRACT
        @errors << "approved manifest contract has been changed"
      end
      unless Array(@contract["scene_types"]) == APPROVED_SCENE_TYPES
        @errors << "approved scene type contract has been changed"
      end

      policy = @contract["field_policy"] || {}
      invalid_categories = policy.values - ALLOWED_FIELD_POLICIES
      unless invalid_categories.empty?
        @errors << "field policy contains unsupported categories: #{invalid_categories.uniq.inspect}"
      end
      unless policy == APPROVED_FIELD_POLICY
        @errors << "field policy does not match the approved Unit4 mapping"
      end

      unless Array(@contract["design_tags"]) == APPROVED_DESIGN_TAGS
        @errors << "design tag contract does not match the approved Unit4 vocabulary"
      end
      unless Array(@contract["persistent_inputs"]) == APPROVED_PERSISTENT_INPUTS
        @errors << "approved persistence contract has been changed"
      end
      unless @contract["identity_lock"] == APPROVED_IDENTITY_CONTRACT
        @errors << "approved identity contract has been changed"
      end
      unless @contract["non_progress_records"] == APPROVED_NON_PROGRESS_CONTRACT
        @errors << "approved non-progress contract has been changed"
      end
      unless @contract["ending_sequence"] == APPROVED_ENDING_CONTRACT
        @errors << "approved ending contract has been changed"
      end
    end

    def validate_field_policy
      policy = @contract.fetch("field_policy", {})
      @states.each do |loop_number, state|
        state.keys.each do |key|
          next if policy.key?(key)

          @errors << "loop#{loop_number} has unclassified top-level field: #{key}"
        end
      end
    end

    def validate_known_facts_chain
      inherited = []
      @states.each do |loop_number, state|
        actual = Array(state.dig("player_context", "known_facts"))
        unless actual == inherited
          @errors << "loop#{loop_number} known facts inheritance does not exactly match prior post-expose knowledge"
        end
        inherited += Array(state.dig("player_context", "post_expose_knowledge"))
      end
    end

    def validate_scene_types
      allowed = Array(@contract["scene_types"])
      @states.each do |loop_number, state|
        scene_groups = [["scene", Array(state["scenes"])]]
        if loop_number == 5
          scene_groups << ["ending scene", Array(state.dig("ending_sequence", "scenes"))]
        end

        scene_groups.each do |label, scenes|
          scenes.each do |scene|
            unless allowed.include?(scene["type"])
              @errors << "loop#{loop_number} #{label} #{scene["id"]} has unsupported scene type: #{scene["type"].inspect}"
            end

            Array(scene["design_tags"]).each do |tag|
              next if APPROVED_DESIGN_TAGS.include?(tag)

              @errors << "loop#{loop_number} #{label} #{scene["id"]} has unsupported design tag: #{tag.inspect}"
            end
          end
        end
      end
    end

    def validate_identity_lock
      loop_number = @contract.dig("identity_lock", "loop")
      state = @states[loop_number]
      identity = state.dig("special_mechanics", "identity_lock")
      unless identity
        @errors << "loop#{loop_number} identity_lock is missing"
        return
      end

      @errors << "identity_lock open_questions are not allowed in executable State" if identity.key?("open_questions")
      unless identity["replaces_standard_doubts"] == true
        @errors << "identity_lock must replace standard doubts"
      end
      @errors << "loop5 must not define ordinary doubts" if state.key?("doubts")

      expected = @contract["identity_lock"]
      gate = identity["gate_contract"] || {}
      interaction = identity["interaction_contract"] || {}

      unless identity["status"] == expected["status"]
        @errors << "identity_lock status must remain #{expected["status"].inspect}"
      end
      unless interaction["lanes"] == expected["lanes"]
        @errors << "identity_lock lanes must remain #{expected["lanes"].inspect}"
      end
      unless interaction["slots"] == expected["slots"]
        @errors << "identity_lock slots must remain #{expected["slots"].inspect}"
      end
      unless gate["standard_doubt_progress_required"] == expected["standard_doubt_progress_required"]
        @errors << "identity_lock standard doubt progress gate must be disabled"
      end
      unless gate["completion_condition"] == expected["completion_condition"] &&
             gate["unlocks"] == expected["unlocks"]
        @errors << "identity_lock gate contract must unlock expose after all chains complete"
      end

      unless interaction["chain_open_order"] == expected["chain_open_order"] &&
             interaction["submission"] == expected["submission"]
        @errors << "identity_lock interaction contract does not match the approved B behavior"
      end

      expected_wrong = expected["wrong_submission"] || {}
      actual_wrong = interaction["wrong_submission"] || {}
      expected_wrong.each do |key, value|
        next if actual_wrong[key] == value

        @errors << "identity_lock wrong submission contract mismatch: #{key}"
      end

      chains = Array(identity["chains"])
      chain_ids = chains.map { |chain| chain["id"] }
      unless chain_ids == Array(expected["chain_ids"])
        @errors << "identity_lock chain IDs must be #{Array(expected["chain_ids"]).inspect}"
      end
      unless identity["completion_condition"] == expected["completion_condition"] &&
             identity["unlocks"] == expected["unlocks"]
        @errors << "identity_lock completion fields are inconsistent with gate_contract"
      end

      scene_4042 = Array(state["scenes"]).find { |scene| scene["id"] == 4042 }
      mickey_returns = Array(scene_4042&.dig("event_triggers")).find do |trigger|
        trigger["id"] == "mickey_returns"
      end
      unless mickey_returns && mickey_returns["condition"] == expected["mickey_returns_condition"]
        @errors << "mickey_returns must wait for the approved identity completion condition"
      end

      unlock_condition = state.dig("expose", "unlock_condition")
      unless unlock_condition == expected["expose_unlock_condition"]
        @errors << "loop5 expose unlock condition must exactly match the identity lock contract"
      end

      usable = Array(state.dig("expose", "rounds")).flat_map do |round|
        Array(round["usable_evidence"]).map { |entry| entry["id"] }
      end.compact.uniq
      chain_inputs = chains.flat_map { |chain| Array(chain["inputs"]).map { |entry| entry["id"] } }.uniq
      missing = usable - chain_inputs
      unless missing.empty?
        @errors << "loop5 expose usable evidence is not covered by identity chains: #{missing.inspect}"
      end
    end

    def validate_persistence
      Array(@contract["persistent_inputs"]).each do |rule|
        state = @states[rule["source_loop"]]
        registry = Array(state[rule["registry"]])
        entry = registry.find { |candidate| candidate["id"] == rule["id"] }
        unless entry
          @errors << "persistence source #{rule["id"]} missing from loop#{rule["source_loop"]} #{rule["registry"]}"
          next
        end

        persistence = entry["persistence"] || {}
        unless persistence["scope"] == "chapter" &&
               persistence["reset_policy"] == "retain_across_loops" &&
               Array(persistence["required_by"]) == Array(rule["required_by"])
          @errors << "persistence contract mismatch for #{rule["id"]}"
        end

        inherited = Array(@states[5]["evidence_registry"]).find { |candidate| candidate["id"] == rule["id"] }
        unless inherited && inherited["inherited"] == true && inherited["source_loop"] == rule["source_loop"]
          @errors << "loop5 inherited registry entry missing or inconsistent for #{rule["id"]}"
        end

        Array(rule["required_by"]).each do |consumer|
          next if persistence_consumer_present?(consumer, rule["id"])

          @errors << "persistence consumer #{consumer} does not reference #{rule["id"]}"
        end
      end
    end

    def persistence_consumer_present?(consumer, id)
      loop5 = @states[5]
      if consumer.start_with?("identity_lock.chain_")
        chain_id = consumer.delete_prefix("identity_lock.chain_").to_i
        chain = Array(loop5.dig("special_mechanics", "identity_lock", "chains")).find do |entry|
          entry["id"] == chain_id
        end
        return Array(chain&.dig("inputs")).any? { |input| input["id"] == id }
      end

      if consumer == "interaction_letter_safe"
        scene = Array(loop5["scenes"]).find { |entry| entry["id"] == 4042 }
        interaction = Array(scene&.dig("interactions")).find do |entry|
          entry["id"] == "interaction_letter_safe"
        end
        return interaction && interaction["input_source"] == id
      end

      false
    end

    def validate_non_progress_records
      rule = @contract["non_progress_records"]
      records = Array(@states[rule["loop"]]["non_progress_investigation_records"])
      unless records.map { |record| record["id"] } == Array(rule["ids"])
        @errors << "non-progress record IDs do not match contract"
      end

      expected = rule["presentation"]
      records.each do |record|
        next if record["presentation"] == expected

        @errors << "non-progress record #{record["id"]} presentation contract mismatch"
      end

      if @states[rule["loop"]].key?("doubt_progress")
        @errors << "non-progress record enters ordinary progress: loop3 must not define doubt_progress"
      end

      prohibited_nodes = [
        @states[rule["loop"]]["doubts"],
        @states[rule["loop"]].dig("expose", "unlock_condition")
      ]
      referenced_values = prohibited_nodes.flat_map { |node| scalar_values(node) }.map(&:to_s)
      Array(rule["ids"]).each do |id|
        reference_pattern = /(?:^|[^A-Za-z0-9_])#{Regexp.escape(id.to_s)}(?:$|[^A-Za-z0-9_])/
        next unless referenced_values.any? { |value| value.match?(reference_pattern) }

        @errors << "non-progress record enters ordinary progress or Expose gate: #{id}"
      end
    end

    def validate_ending_sequence
      expected = @contract["ending_sequence"]
      ending = @states[expected["owner_loop"]]["ending_sequence"] || {}
      runtime = ending["runtime_contract"] || {}

      {
        "counts_as_loop" => expected["counts_as_loop"],
        "inherit_loop" => expected["owner_loop"],
        "chapter_end_after" => expected["chapter_end_after"],
        "next_unit_entry" => expected["next_unit_entry"]
      }.each do |key, value|
        next if runtime[key] == value

        @errors << "ending runtime contract mismatch: #{key}; expected #{value.inspect}, got #{runtime[key].inspect}"
      end

      scene_ids = Array(ending["scenes"]).map { |scene| scene["id"] }
      required = %w[ending_4043 ending_4044 ending_4045]
      @errors << "ending sequence must contain #{required.inspect}" unless scene_ids == required

      Array(ending["scenes"]).first(2).each do |scene|
        next unless scene["chapter_end"] == true

        @errors << "early ending scene #{scene["id"]} must not end the chapter"
      end

      final_scene = Array(ending["scenes"]).find { |scene| scene["id"] == "ending_4045" }
      unless final_scene && final_scene["hard_stop"] == true && final_scene["final_frame"].to_s.include?("门外")
        @errors << "ending_4045 must hard-stop outside O'Hara's house"
      end

      first_action = ending.dig("unit4_to_unit5_boundary", "unit5_first_allowed_action")
      unless first_action == expected["unit5_first_allowed_action"]
        @errors << "unit5 first allowed action does not match the approved boundary"
      end

      validate_unit5_outline_boundary(expected)
    end

    def validate_unit5_outline_boundary(expected)
      chapter = Array(@manifest["chapters"]).find { |entry| entry["canonicalUnit"] == "Unit5" }
      outline = chapter&.dig("sources", "outline")
      path = outline && File.join(@root, outline)
      unless path && File.exist?(path)
        @errors << "Unit5 active outline is missing for boundary validation"
        return
      end

      text = File.read(path, encoding: "UTF-8")
      lines = text.lines
      heading_index = lines.index { |line| line.strip == "## 零、承接 Unit4 门外结尾" }
      section_lines = if heading_index
                        lines[(heading_index + 1)..].take_while { |line| !line.start_with?("## ") }
                      else
                        []
                      end
      first_action = section_lines.find { |line| line.start_with?("- ") }&.strip
      expected_prefix = "- #{expected["unit5_outline_first_action_prefix"]}"

      unless text.include?("Unit4 停在 Zack 与 Emma 抵达 O'Hara 家门外") &&
             first_action&.start_with?(expected_prefix)
        @errors << "Unit5 active outline no longer matches the approved Unit4 boundary"
      end
    end

    def scalar_values(value)
      case value
      when Hash
        value.flat_map { |key, child| [key, *scalar_values(child)] }
      when Array
        value.flat_map { |child| scalar_values(child) }
      when nil
        []
      else
        [value]
      end
    end

    def state_path(loop_number)
      File.join(@state_dir, "loop#{loop_number}_state.yaml")
    end
  end
end

if $PROGRAM_NAME == __FILE__
  root = File.expand_path("../../..", __dir__)
  result = Unit4StateContract::Validator.new(root: root).validate
  if result.errors.empty?
    puts "PASS Unit4 state contract validation"
    exit 0
  end

  warn "Unit4 State contract: FAIL"
  result.errors.each { |error| warn "- #{error}" }
  exit 1
end
