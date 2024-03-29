from .RemoteData import *

class Quest:
    def __init__(self, name):
        self.name = name
        self.errors = []
        self.notices = []
        self.summary = ""
        self.summary_extra = ""
        self.prereq = ""
        self.preface = ""
        self.midway_text = ""
        self.objectives = ""
        self.rewards = ""
        self.success = ""

    def description(self, text):
        self.summary = "==Summary==\n" + text + "\n\n"

    def requirements(self, data):
        for req in data:
            if req["T"] == "MinFavorLevel":
                self.prereq += "The quest is available at {{Favor|%s}} favor. " % Favor.get_alias(req["Level"])
            elif req["T"] == "MinSkillLevel":
                self.prereq += "This quest is available at [[%s]] level %s. " % (Skill.get_alias(req["Skill"]), req["Level"])
            elif req["T"] == "QuestCompleted":
                other_quest_name = QuestList.find_quest_by_internalname(req["Quest"])["Name"]
                self.prereq += "You must have previously completed [[%s]] in order to undertake this quest. " % other_quest_name
            elif req["T"] == "HasEffectKeyword" and req["Keyword"] == "LiveEvent_Crafting":
                self.prereq += "This quest is only available during a Crafting Caravan event. "
            elif req["T"] == "HasEffectKeyword" and req["Keyword"] == "LiveEvent_CivilService":
                self.prereq += "This quest is only available during a Civil Service event. "
            elif req["T"] == "HasEffectKeyword" and req["Keyword"] == "LiveEvent_BunFu":
                self.prereq += "This quest is only available during a BunFu event. "
            elif req["T"] == "HasEffectKeyword" and req["Keyword"] == "LiveEvent_LostScapegoats":
                self.prereq += "This quest is only available during a Lost Scapegoats event. "
            elif req["T"] == "HasEffectKeyword" and req["Keyword"] == "LiveEvent_Gobblejack":
                self.prereq += "This quest is only available during a Gobblejack event. "
            elif req["T"] == "IsWarden":
                self.prereq += "This quest is only available for Wardens. "
            elif req["T"] == "AreaEventOn":
                self.prereq += "This quest is only available during an event in the area. "
                # check req["AreaEvent"]
            elif req["T"] == "AreaEventOff":
                if req["AreaEvent"] == "PovusNightlyQuest":
                    self.prereq += "This quest is only available during daytime. "
                else:
                    self.prereq += "This quest is only available outside an event in the area. "
            elif req["T"] == "HangOutCompleted":
                self.prereq += "This quest is only available after completing a hangout. "
                # check req["HangOut"]
            elif req["T"] == "InteractionFlagSet":
                # check req["InteractionFlag"]
                self.prereq += "This quest is only available after an interaction. "
            elif req["T"] == "GuildQuestCompleted":
                other_quest_name = QuestList.find_quest_by_internalname(req["Quest"])["Name"]
                self.prereq += "You must have previously completed [[%s]] in order to undertake this quest. " % other_quest_name
            elif req["T"] == "Or":
                # Hopefully this is only used for event quests
                self.notices.append("Or-Requirement needs manual check")
            elif req["T"] == "IsLongtimeAnimal":
                self.prereq += "This quest is only available to long time animals. "
            elif req["T"] == "Race":
                self.prereq += "This quest is only available to {}. ".format(req["AllowedRace"])
            elif req["T"] == "ScriptAtomicMatches":
                if "AtomicVar" in req and req["AtomicVar"] == "PovusNightState":
                    self.prereq += "This quest is only available at night. "
                else:
                    self.errors.append("Unknown requirement sub type " + req["T"])
            else:
                self.errors.append("Unknown requirement type " + req["T"])

    def generate_wiki_source(self):
        self.errors = []
        data = QuestList.find_quest_by_name(self.name)

        try:
            if "FavorNpc" not in data or data["FavorNpc"] == "":
                npc = None
                area_alias = data["DisplayedLocation"] if "DisplayedLocation" in data else None
                area_prefix = None
            else:
                npc = NpcList.find_npc_by_ref(data["FavorNpc"])
                area = npc.area
                area_alias = area.get_alias()
                area_prefix = area.get_prefix()
        except KeyError:
            self.errors.append("NPC not found")
            npc = Npc(data["FavorNpc"], AreaList.find_by_areaname(data["DisplayedLocation"]))
            area = npc.area
            area_alias = area.get_alias()
            area_prefix = area.get_prefix()

        if "DisplayedLocation" in data:
            # Some areas have a good display location, some don't. Overwrite when we know it is nice.
            if data["DisplayedLocation"] == "Sacred Grotto":
                area_alias = data["DisplayedLocation"]
                area_prefix = "the "

        for key in data:
            if key == "InternalName" or key == "IsCancellable" or key == "Name" or key == "Version":
                pass  # Tech stuff
            elif key == "FavorNpc" or key == "DisplayedLocation":
                pass  # NPC is handled above
            elif key == "TSysLevel":
                pass  # Not sure what that is. I don't think we should display it.
            elif key == "GroupingName":
                pass  # Tech value to group quests so you can only have one of the group. Like casino daily.
            elif key == "Level":
                pass  # Druid event, also NumExpectedParticipants
            elif key == "IsGuildQuest" or key == "NumExpectedParticipants" or key == "IsAutoWrapUp" or key == "IsAutoPreface" or key == "ReuseTime_Minutes":
                pass  # Guild quest stuff
            elif key == "Keywords":
                pass  # This might be interesting, but only used for guild quests atm?
            elif key == "RequirementsToSustain":
                pass  # Probably used to auto-cancel quests after events like halloween
            elif key == "PreGiveItems" or key == "PreGiveRecipes" or key == "PreGiveEffects":
                pass
            elif key == "Description":
                self.description(data[key])
            elif key == "MidwayText":
                self.midway_text = "===Midway===\n" + data["MidwayText"].strip() + "\n\n"
            elif key == "ReuseTime_Days":
                self.summary_extra += "This Quest can be repeated after {} day{}.\n\n".format(data["ReuseTime_Days"], '' if data["ReuseTime_Days"] == 1 else 's')
            elif key == "ReuseTime_Hours":
                self.summary_extra += "This Quest can be repeated after {} hour{}.\n\n".format(data["ReuseTime_Hours"], '' if data["ReuseTime_Hours"] == 1 else 's')
            elif key == "Requirements":
                if type(data["Requirements"]) is dict:
                    self.requirements([data["Requirements"]])
                elif type(data["Requirements"][0]) is list:
                    # This is a AND combination of sub-requirements
                    for item in data["Requirements"]:
                        self.requirements(item)
                else:
                    self.requirements(data["Requirements"])
            elif key == "PrefaceText":
                self.preface = "===Preface===\n" + data["PrefaceText"].strip() + "\n\n"
            elif key == "Objectives":
                for item in data["Objectives"]:
                    self.objectives += "* " + item["Description"]  # TODO item linking if item["ItemName"] and item["Type"] == "Collect"
                    if "Number" in item and item["Number"] > 1 and item["Description"].find(str(item["Number"])) == -1:
                        self.objectives += " x%i" % item["Number"]
                    self.objectives += "\n"
            elif key == "SuccessText":
                self.success = "{{Quote|" + data["SuccessText"] + "}}\n"
            elif key == "Reward_Favor":
                self.rewards += "* %i {{Favor|favor}}\n" % data["Reward_Favor"]
            elif key == "Reward_Gold":
                self.rewards += "* %i councils\n" % data["Reward_Gold"]
            elif key == "Rewards_Currency":
                for curr in data["Rewards_Currency"]:
                    if curr == "WardenPoints":
                        self.rewards += "* %i Warden Points\n" % data["Rewards_Currency"]["WardenPoints"]
                    elif curr == "Gold":
                        self.rewards += "* %i councils\n" % data["Rewards_Currency"]["Gold"]
                    else:
                        self.errors.append("Unknown reward currency in " + data["InternalName"])
            elif key == "Rewards_Items":
                for item in data["Rewards_Items"]:
                    self.rewards += "* {{Item|" + Item.get_name_for_internal(item["Item"]) + "}}"
                    if item["StackSize"] > 1:
                        self.rewards += " x%i" % item["StackSize"]
                    self.rewards += "\n"
            elif key == "Rewards":
                # Rewards is a list, maybe sometimes a dict?
                for reward in data["Rewards"]:
                    if reward["T"] == "SkillXP" or reward["T"] == "SkillXp":  # Inconsistent uppercase
                        self.rewards += "* {} XP in {}\n".format(reward["Xp"], SkillList.find_by_internalname(reward["Skill"]).name)
                    elif reward["T"] == "Recipe":
                        self.rewards += "* Recipe: {}\n".format(RecipeList.find_by_name(reward["Recipe"]).name)
                    elif reward["T"] == "GuildXp":
                        self.rewards += "* {} Guild XP\n".format(reward["Xp"])
                    elif reward["T"] == "GuildCredits":
                        self.rewards += "* {} Guild Credits\n".format(reward["Credits"])
                    elif reward["T"] == "CombatXp":
                        self.rewards += "* {} Combat XP for your active skills\n".format(reward["Xp"])
                    elif reward["T"] == "Currency":
                        self.rewards += "* {} {}\n".format(reward["Amount"], reward["Currency"])
                    else:
                        self.errors.append("Unexpected reward type " + reward["T"])
            elif key == "Rewards_Effects":
                self.notices.append("Special reward effect for quest {} must be handled manually".format(data["InternalName"]))
            elif key == "Rewards_NamedLootProfile":
                self.rewards += "* random items\n"  # Special loot table for rewards
            elif key == "Rewards_XP":
                for item in data["Rewards_XP"]:
                    self.rewards += "* {} XP in {}\n".format(data["Rewards_XP"][item], SkillList.find_by_internalname(item).name)
            elif key == "FollowUpQuests":
                pass # do we display these?
            else:
                self.errors.append("Unhandled key {} in quest data".format(key))

        result = "__NOTOC__\n"
        result += self.summary + self.summary_extra

        if npc:
            result += "===Prerequisites===\n"
            result += "To start this quest, talk to '''[[%s]]''' in %s'''[[%s]]'''. " % (npc.get_name(), area_prefix, area_alias)

        result += self.prereq + "\n\n"
        result += self.preface

        result += self.midway_text

        result += "===Requirements===\n"
        result += self.objectives + "\n"

        result += "===Rewards===\n"
        result += "{{Spoiler|Rewards|\n"
        result += self.success
        result += self.rewards + "}}\n\n"

        result += "[[Category:Quests]]"
        if area_alias:
            result += "[[Category:Quests/%s Quests]]" % area_alias
        if npc:
            result += "[[Category:Quests/%s]]" % npc.get_name()
        return result + "\n"

    def get_errors(self):
        return self.errors

    def get_notices(self):
        return self.notices


class Favor:
    @staticmethod
    def get_alias(name):
        return re.sub(r'(.)([A-Z])', r'\1 \2', name)


class Skill:
    @staticmethod
    def get_alias(name):
        if name == "Race_Fae":
            return "Fae (Race Skill)"
        return re.sub(r'(.)([A-Z])', r'\1 \2', name)

